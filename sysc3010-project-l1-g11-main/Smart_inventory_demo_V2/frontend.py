import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os
import cv2
import flask
import time
import numpy as np
from picamera2 import Picamera2
from backend import Backend, logger
from mydbconfig import *

# Initialize Flask app for video streaming
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

# Initialize Backend
backend = Backend(config, email, firstname, lastname)

# Get available cameras
camera_info = Picamera2.global_camera_info()
camera_indices = list(range(len(camera_info)))

# Active camera instance
active_camera = None

def release_camera():
    """Ensure the active camera is fully released before switching."""
    global active_camera
    if active_camera:
        try:
            logger.info("Stopping active camera...")
            active_camera.stop()
            active_camera.close()
            time.sleep(1)  # Allow time for the OS to release it
            active_camera = None
            logger.info("Camera successfully released.")
        except Exception as e:
            logger.warning(f"Error releasing camera: {e}")
            active_camera = None


def initialize_camera(cam_index):
    """Safely initialize a camera, ensuring it's not already running."""
    global active_camera

    # If a camera is already running with the same index, do nothing
    if active_camera and active_camera.camera_num == cam_index:
        logger.info(f"Camera {cam_index} is already running. Skipping initialization.")
        return

    # Release any previously active camera
    release_camera()

    try:
        camera_info = Picamera2.global_camera_info()
        if cam_index >= len(camera_info):
            logger.error(f"Camera index {cam_index} is out of range! Available cameras: {camera_info}")
            return  # Prevent invalid index initialization

        # Initialize and start the new camera
        active_camera = Picamera2(cam_index)
        active_camera.configure(active_camera.create_video_configuration(main={"size": (640, 480)}))
        active_camera.start()
        logger.info(f"Camera {cam_index} initialized successfully.")

    except RuntimeError as e:
        logger.error(f"Failed to initialize camera {cam_index}: {e}")
        active_camera = None  # Prevent keeping a broken camera instance

def generate_frames():
    """Capture frames from the active camera."""
    while True:
        if active_camera:
            frame = active_camera.capture_array()
            _, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@server.route("/video_feed")
def video_feed():
    return flask.Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

# Get authorized devices
my_devices = backend.get_my_devices() or []

if not my_devices:
    raise ValueError("No devices available for this user.")

header = html.H1("Smart Inventory System - Camera")
subheader = html.H4(", ".join([f"{backend.get_device_owner(id)}" for id in my_devices]))

dropdown = dcc.Dropdown(
    id='camera_dropdown',
    options=[{'label': f'Camera {i}', 'value': i} for i in camera_indices],
    value=camera_indices[0] if camera_indices else None
)

video_display = html.Img(id="video-feed", src="/video_feed", style={"width": "50%"})

app.layout = html.Div([
    header,
    subheader,
    dropdown,
    video_display
])

@app.callback(
    Output("video-feed", "src"),
    Input("camera_dropdown", "value")
)
def update_video_feed(cam_index):
    """Switch the active camera when the dropdown changes."""
    if cam_index is not None:
        initialize_camera(cam_index)
    return "/video_feed"

if __name__ == "__main__":
    if camera_indices:
        initialize_camera(camera_indices[0])  # Start first camera safely
    app.run_server(debug=True, host='0.0.0.0')

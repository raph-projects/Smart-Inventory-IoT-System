import cv2
import time
from picamera2 import Picamera2
from tflite_support.task import core, processor, vision
import utils

class Detect:
    def __init__(self):
        self.model = 'efficientdet_lite0.tflite'  # Set model
        self.num_threads = 3

        self.dispW = 720
        self.dispH = 480

        # Initialize PiCamera2
        self.picam2 = Picamera2()
        self.picam2.preview_configuration.main.size = (self.dispW, self.dispH)
        self.picam2.preview_configuration.main.format = 'RGB888'
        self.picam2.preview_configuration.align()
        self.picam2.configure("preview")

        # Initialize Webcam
        self.webCam = '/dev/video2'
        self.cam = cv2.VideoCapture(self.webCam)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.dispW)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.dispH)
        self.cam.set(cv2.CAP_PROP_FPS, 30)

        # Assert model file
        assert self.model.endswith('.tflite'), "Model file should be a .tflite file"
        assert self.cam.isOpened(), "Failed to open webcam"

        # Text properties
        self.pos = (20, 60)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.height = 1.5
        self.weight = 3
        self.myColor = (255, 0, 0)

        # Load Object Detection Model
        base_options = core.BaseOptions(file_name=self.model, use_coral=False, num_threads=self.num_threads)
        detection_options = processor.DetectionOptions(max_results=4, score_threshold=0.3)
        options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
        self.detector = vision.ObjectDetector.create_from_options(options)

        assert self.detector is not None, "Object detector initialization failed"

    def is_duplicate(new_obj, existing_data, iou_threshold=0.7):
      """
      Checks if the detected object is already in the database.
      - Compares object class and bounding box similarity.
      - Uses Intersection over Union (IoU) to measure overlap.
      """
      for key, existing_obj in existing_data.items():
          if existing_obj["class_id"] == new_obj["class_id"]:  # Same object type
              # Calculate Intersection over Union (IoU)
              if iou(existing_obj["bounding_box"], new_obj["bounding_box"]) > iou_threshold:
                  return True  # Object is already detected
      return False  # Not a duplicate
      

    def detect_obj(self, num_frames=5):
      self.picam2.start()  # Start the camera
      detected_objects = []  # List to hold detected objects
      fps = 0
      tStart = time.time()

      for _ in range(num_frames):  # Loop to capture a specific number of frames
          ret, im = self.cam.read()  # Read a frame from the camera
          if not ret or im is None:
              print("Frame capture failed")
              continue

          # Process the frame
          im = cv2.flip(im, -1)  # Flip the image
          imRGB = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)  # Convert to RGB
          imTensor = vision.TensorImage.create_from_array(imRGB)  # Create tensor image
          detections = self.detector.detect(imTensor)  # Detect objects

          # Extracting data from detections
          for detection in detections.detections:  # Assuming detections has a list of detected objects
              for category in detection.categories:  # Iterate through categories
                  detected_info = {
                      "class_id": category.index,  # Use category index as class ID
                      "name": category.display_name or category.category_name,  # Get object name
                      "score": category.score,  # Use category score
                      "bounding_box": {
                          "left": detection.bounding_box.origin_x,
                          "top": detection.bounding_box.origin_y,
                          "right": detection.bounding_box.origin_x + detection.bounding_box.width,
                          "bottom": detection.bounding_box.origin_y + detection.bounding_box.height
                      }
                  }
                  detected_objects.append(detected_info)

          # Optional: Visualize the detections
          im = utils.visualize(im, detections)  # Visualize the detections

          # Display FPS
          tEnd = time.time()
          loopTime = max(tEnd - tStart, 1e-6)  # Prevent division by zero
          fps = 0.9 * fps + 0.1 * (1 / loopTime)
          tStart = time.time()

          # Display FPS on the image
          cv2.putText(im, f"{int(fps)} FPS", self.pos, self.font, self.height, self.myColor, self.weight)
          cv2.imshow('Camera', im)

          if cv2.waitKey(1) == ord('q'):
              break

      self.picam2.stop()  # Stop the camera
      return detected_objects  # Return the collected detected objects

      self.cam.release()
      cv2.destroyAllWindows()

if __name__ == "__main__":
    obj = Detect()
    obj.detect_obj()

from sense_hat import SenseHat
from backend import Backend, logger
from mydbconfig import *
import time

sense = SenseHat()

def init_screen(backend):
    if backend.is_device():
        colors = backend.get_led_status(backend._device_info['serial'])
        sense.set_pixels(colors)
    else:
        raise Exception("This is not a Raspberry pi. This file should be run from a RPi.")

def led_stream_handler(message):
    if message['event'] == 'put':
        if message['path'][1:].isnumeric():
            ledn = int(message['path'][1:])
            color = message['data']
            sense.set_pixel(
                (ledn - 1) % 8,
                int((ledn - 1) / 8),
                message['data'][0],
                message['data'][1],
                message['data'][2],
            )
            logger.debug(f"Received update for led: {message}")

def monitor_joystick(backend):
    device_id = backend.get_device_id()
    while True:
        for event in sense.stick.get_events():
            if event.action == "pressed":
                logger.debug("Joystick pressed, clearing LEDs.")
                backend.clear_leds(device_id)
        time.sleep(0.1)  # Prevents excessive CPU usage

def main():
    # Initialize the db with configuration and user data
    backend = Backend(config, email, firstname, lastname)

    # Initialize the LED values from database
    init_screen(backend)

    # Register a stream: whenever there is a change, execute the function led_stream_handler()
    led_stream = backend._db \
        .child('devices') \
        .child(backend._device_info['serial']) \
        .child('leds') \
        .stream(led_stream_handler)
    
    # Start monitoring joystick for presses
    monitor_joystick(backend)

if __name__ == '__main__':
    main()


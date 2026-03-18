import RPi.GPIO as GPIO
import time

# Define the buzzer pin
BUZZER_PIN = 16  # Change this to the correct GPIO pin

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# PWM for tone control
pwm = GPIO.PWM(BUZZER_PIN, 2000)  # 1kHz frequency (adjust as needed)


def beep(delayms):
    """Function to make a beep sound for a given duration (in milliseconds)."""
    pwm.start(50)  # Simulates analogWrite with 20% duty cycle
    time.sleep(delayms / 1000.0)  # Convert ms to seconds
    pwm.stop()
    time.sleep(delayms / 1000.0)  # Delay before next beep


# Initial beeps
beep(50)
beep(50)
time.sleep(1)  # Delay 1 second

print("Stopping buzzer...")
pwm.stop()
GPIO.cleanup()  # Clean up GPIO pins


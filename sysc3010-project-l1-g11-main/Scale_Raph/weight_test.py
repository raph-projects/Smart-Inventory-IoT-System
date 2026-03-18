import RPi.GPIO as GPIO
from hx711 import HX711
import time

# ──────────────── Setup Load Cell ──────────────── #
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin=6, pd_sck_pin=5)

# ──────────────── Zero the Scale ──────────────── #
input("Make sure the scale is empty, then press Enter to zero the scale.")
hx.zero()
print("Scale zeroed.")

# ──────────────── Calibrate ──────────────── #
input("Place a known weight on the scale and press Enter.")
reading = hx.get_data_mean(readings=100)
known_weight = float(input("Enter the known weight in grams: "))
ratio = reading / known_weight
hx.set_scale_ratio(ratio)
print(f"Calibration complete. Ratio set to {ratio:.2f}")

# ──────────────── Print Live Weight ──────────────── #
print("\nStarting live weight display. Press Ctrl+C to exit.\n")

try:
    while True:
        weight = hx.get_weight_mean(readings=10)
        print(f"Weight: {weight:.2f} g     ", end='\r')
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting...")
    GPIO.cleanup()

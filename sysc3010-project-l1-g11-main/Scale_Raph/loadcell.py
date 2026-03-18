import RPi.GPIO as GPIO
from hx711 import HX711
import time
import pyrebase

# ──────────────── Firebase Configuration ──────────────── #
config = {
    "apiKey": "AIzaSyCxXKQE9ietlYXU9Sm5qzXLb27G1xR0prs", 
    "authDomain": "lab3-8f22c.firebaseapp.com", 
    "databaseURL": "https://lab3-8f22c-default-rtdb.firebaseio.com/", 
    "storageBucket": "lab3-8f22c.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
username = "raphael"
dataset = "Smart_Scale_Simple"

# ──────────────── Setup Load Cell ──────────────── #
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin=6, pd_sck_pin=5)

# ──────────────── Zero Before Calibration ──────────────── #
input("Make sure the scale is empty, then press Enter to zero the scale.")
hx.zero()
print("Scale zeroed.")

# ──────────────── Calibrate with Known Weight ──────────────── #
input("Place a known weight on the scale and press Enter: ")
reading = hx.get_data_mean(readings=100)
known_weight_grams = float(input("Enter the known weight in grams: "))
ratio = reading / known_weight_grams
hx.set_scale_ratio(ratio)
print(f"Calibration ratio set: {ratio:.2f}")

# ──────────────── Calibrate Each Item Once ──────────────── #
item_weights = {}
tolerance = 3  # ±3 grams
num_items = int(input("\nHow many unique items do you want to calibrate? "))

for i in range(num_items):
    name = input(f"\nEnter name of item {i+1}: ")
    input(f"Place one '{name}' on the scale and press Enter: ")
    weight = hx.get_weight_mean(readings=100)
    item_weights[name] = weight
    print(f"'{name}' weight recorded: {weight:.2f} g (±{tolerance} g)")
    input("Remove the item and press Enter to continue...")

print("\nReading initial baseline weight...")
prev_weight = hx.get_weight_mean(readings=30)
print(f"Baseline set to: {prev_weight:.2f} g")
print("\nStarting live detection...\n")

# ──────────────── Runtime Logic ──────────────── #
item_counts = {name: 0 for name in item_weights}

def detect_object_type(delta, item_weights, tolerance):
    best_match = None
    best_count = 0
    best_diff = float('inf')

    for name, weight in item_weights.items():
        n = round(delta / weight)
        estimated = n * weight
        diff = abs(estimated - delta)

        if n > 0 and diff <= tolerance:
            if diff < best_diff:
                best_match = name
                best_count = n
                best_diff = diff

    return best_match, best_count

try:
    while True:
        current_weight = hx.get_weight_mean(readings=20)

        # ──────────────── Auto-reset if scale is empty ──────────────── #
        if abs(current_weight) < 1.0:
            if any(item_counts.values()):
                item_counts = {name: 0 for name in item_weights}
                db.child(username).child(dataset).set(item_counts)
                print("\nScale is empty — resetting all counts to 0.")
            prev_weight = current_weight
            time.sleep(0.6)
            continue

        # ──────────────── Normal detection logic ──────────────── #
        delta = current_weight - prev_weight

        if abs(delta) > 2.0:  # Ignore tiny fluctuations
            direction = "added" if delta > 0 else "removed"
            delta_abs = abs(delta)

            name, count = detect_object_type(delta_abs, item_weights, tolerance)

            if name:
                if delta > 0:
                    item_counts[name] += count
                    print(f"\nDetected {count} '{name}' added. Total: {item_counts[name]}")
                else:
                    item_counts[name] = max(0, item_counts[name] - count)
                    print(f"\nDetected {count} '{name}' removed. Total: {item_counts[name]}")

                db.child(username).child(dataset).set(item_counts)
                prev_weight = current_weight
            else:
                print(f"\nUnrecognized object(s), delta: {delta:.2f} g")

        else:
            print(f"Waiting... Current: {current_weight:.2f} g     ", end='\r')

        time.sleep(0.6)

except KeyboardInterrupt:
    print("\nExiting...")
    GPIO.cleanup()


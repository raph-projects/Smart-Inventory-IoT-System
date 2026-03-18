import time
import threading
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
from database import db

# === GPIO & LCD Setup ===
GPIO.setwarnings(False)
BUZZER_PIN = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
pwm = GPIO.PWM(BUZZER_PIN, 5000)

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2)

# === Firebase Paths ===
AGRIM_PATH = ("agrim", "Object_Count")
RAPH_PATH = ("raphael", "Smart_Scale_Simple")
ULTRASONIC_PATH = ("Abderrezak", "Ultrasonic_Sensor")

# === Configs ===
UNIVERSAL_THRESHOLD = 1
DISTANCE_TRIGGER_THRESHOLD = 45 # cm

# Shared state
last_inventory = {}
stop_display = threading.Event()
processed_keys = set()

# === Utility Functions ===
def beep(delayms):
    pwm.start(50)
    time.sleep(delayms / 1000.0)
    pwm.stop()
    time.sleep(delayms / 1000.0)

def write_lcd_lines(line1="", line2=""):
    lcd.clear()
    lcd.write_string(line1.ljust(16))
    lcd.crlf()
    lcd.write_string(line2.ljust(16))

# === Inventory Fetching ===
def get_inventory():
    inventory = {}

    agrim_data = db.child(*AGRIM_PATH).get()
    agrim_val = agrim_data.val()

    if isinstance(agrim_val, list):
        for data in agrim_val:
            if data is None:
                continue
            name = data.get("name", "unknown")
            if name.lower() in ["person", "refrigerator", "dining table"]:
                continue
            if name.lower() == "vase":
                name = "cup"
            count = data.get("count", 0)
            inventory[name] = inventory.get(name, 0) + count

    elif isinstance(agrim_val, dict):
        for class_id, data in agrim_val.items():
            name = data.get("name", "unknown")
            if name.lower() in ["person", "refrigerator", "dining table"]:
                continue
            if name.lower() == "vase":
                name = "cup"
            count = data.get("count", 0)
            inventory[name] = inventory.get(name, 0) + count

    raph_data = db.child(*RAPH_PATH).get()
    if raph_data.val():
        for name, count in raph_data.val().items():
            inventory[name] = inventory.get(name, 0) + count

    return inventory

# === LCD Inventory Scroller ===
def display_inventory_loop():
    global last_inventory

    while True:
        if stop_display.is_set():
            time.sleep(0.5)
            continue

        current_inventory = get_inventory()
        for item_name, quantity in current_inventory.items():
            if stop_display.is_set():
                break

            write_lcd_lines(f"{item_name}:", f"Qty: {quantity}")
            time.sleep(2)

            if quantity < UNIVERSAL_THRESHOLD:
                beep(100)
                time.sleep(0.2)
                beep(100)
                write_lcd_lines("LOW STOCK:", item_name)
                time.sleep(3)

# === Ultrasonic Trigger Loop (Main Priority Loop) ===
def main_loop():
    global last_inventory

    last_inventory = get_inventory()

    while True:
        try:
            entries = db.child(*ULTRASONIC_PATH).get().val()
            if not entries:
                time.sleep(1)
                continue

            for key, data in sorted(entries.items()):
                if key in processed_keys:
                    continue

                distance = data.get("Distance_cm")
                processed_keys.add(key)

                if distance is not None and distance < DISTANCE_TRIGGER_THRESHOLD:
                    stop_display.set()
                    print(f"Triggered by distance: {distance} cm")

                    time.sleep(3)  # Give Agrim and Raph time to update Firebase
                    current_inventory = get_inventory()

                    for item_name in current_inventory:
                        old_qty = last_inventory.get(item_name, 0)
                        new_qty = current_inventory[item_name]

                        if new_qty > old_qty:
                            write_lcd_lines("Added:", item_name)
                            beep(50)
                            beep(50)
                            time.sleep(2)

                        elif new_qty < old_qty:
                            write_lcd_lines("Removed:", item_name)
                            beep(100)
                            beep(100)
                            time.sleep(2)

                    last_inventory = current_inventory
                    stop_display.clear()
                    break

        except Exception as e:
            print(f"Error reading: {e}")

        time.sleep(1)

# === Backup Checker (in case ultrasonic misses it) ===
def backup_inventory_checker():
    global last_inventory

    while True:
        if stop_display.is_set():
            time.sleep(1)
            continue

        current_inventory = get_inventory()

        for item_name in current_inventory:
            old_qty = last_inventory.get(item_name, 0)
            new_qty = current_inventory[item_name]

            if new_qty > old_qty:
                stop_display.set()
                write_lcd_lines("Added:", item_name)
                beep(50)
                beep(50)
                time.sleep(2)
                stop_display.clear()

            elif new_qty < old_qty:
                stop_display.set()
                write_lcd_lines("Removed:", item_name)
                beep(100)
                beep(100)
                time.sleep(2)
                stop_display.clear()

        last_inventory = current_inventory
        time.sleep(5)  # Backup check interval

# === Run Threads ===
try:
    # Start the inventory scroller
    display_thread = threading.Thread(target=display_inventory_loop, daemon=True)
    display_thread.start()

    # Start the backup checker
    backup_thread = threading.Thread(target=backup_inventory_checker, daemon=True)
    backup_thread.start()

    # Run ultrasonic checker (priority loop)
    main_loop()
    

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()

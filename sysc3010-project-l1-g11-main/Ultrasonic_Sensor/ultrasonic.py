import RPi.GPIO as GPIO
import time
import pyrebase

# === Firebase Setup ===
config = {
    "apiKey": "AIzaSyCxXKQE9ietlYXU9Sm5qzXLb27G1xR0prs",
    "authDomain": "lab3-8f22c.firebaseapp.com",
    "databaseURL": "https://lab3-8f22c-default-rtdb.firebaseio.com/",
    "storageBucket": "lab3-8f22c.appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
username = "Abderrezak"
dataset = "Ultrasonic_Sensor"

# === GPIO Setup ===
TRIG = 23
ECHO = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setwarnings(False)

def measure_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    timeout = time.time() + 0.02
    while GPIO.input(ECHO) == 0:
        if time.time() > timeout:
            return None
    pulse_start = time.time()

    timeout = time.time() + 0.02
    while GPIO.input(ECHO) == 1:
        if time.time() > timeout:
            return None
    pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * 34300) / 2
    return round(distance, 2)

# === Threshold for change (in cm) ===
MIN_CHANGE_THRESHOLD = 5.0
last_uploaded_distance = None

if __name__ == "__main__":
    try:
        while True:
            distance = measure_distance()
            if distance is not None:
                if distance < 10:
                    status = "? Too close!"
                elif distance < 30:
                    status = "? Approaching"
                else:
                    status = "? Safe"

                print(f"{status} Object detected at {distance} cm.")

                # Decide whether to update Firebase
                if (last_uploaded_distance is None or
                    abs(distance - last_uploaded_distance) >= MIN_CHANGE_THRESHOLD):
                    
                    data = {"Distance_cm": distance, "Status": status}

                    try:
                        # Push new reading
                        db.child(username).child(dataset).push(data)
                        print("? Firebase updated.")
                        last_uploaded_distance = distance

                        # Trim list to last 5 entries
                        all_entries = db.child(username).child(dataset).get().val()
                        if all_entries and len(all_entries) > 5:
                            sorted_keys = sorted(all_entries.keys())
                            for key in sorted_keys[:-5]:
                                db.child(username).child(dataset).child(key).remove()

                    except Exception as e:
                        print(f"? Firebase update failed: {e}")
                else:
                    print("?? No significant change. Firebase not updated.")
            else:
                print("?? Sensor timeout.")

            time.sleep(2)

    except KeyboardInterrupt:
        GPIO.cleanup()

import pyrebase
import time
from collections import defaultdict
from detect import Detect
from mydbconfig import config

# ── Firebase Setup ──
# Credentials are loaded from mydbconfig.py (not committed to GitHub).
# Copy mydbconfig.example.py to mydbconfig.py and fill in your credentials.

# Initialize object detection
obj = Detect()

firebase = pyrebase.initialize_app(config)
db = firebase.database()
dataset = "Object_Detection"
count_dataset = "Object_Count"
username = "agrim"

# Reset Firebase database at start
db.child(username).child(dataset).remove()
db.child(username).child(count_dataset).remove()
print(f"Databases {dataset} and {count_dataset} reset successfully!")

# Dictionary to track object counts
object_counts = defaultdict(lambda: {"name": "", "count": 0})

def is_new_object(detected_obj, existing_objects, threshold=50):
    class_id = detected_obj["class_id"]
    bbox = detected_obj["bounding_box"]

    for existing_obj in existing_objects:
        if existing_obj["class_id"] == class_id:
            x1 = bbox["left"] + (bbox["right"] - bbox["left"]) / 2
            y1 = bbox["top"] + (bbox["bottom"] - bbox["top"]) / 2

            existing_bbox = existing_obj["bounding_box"]
            x2 = existing_bbox["left"] + (existing_bbox["right"] - existing_bbox["left"]) / 2
            y2 = existing_bbox["top"] + (existing_bbox["bottom"] - existing_bbox["top"]) / 2

            distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

            if distance < threshold:
                return False

    return True

while True:
    detected_objects = obj.detect_obj()
    new_counts = defaultdict(lambda: {"name": "", "count": 0})
    filtered_objects = []

    for detected_obj in detected_objects:
        if is_new_object(detected_obj, filtered_objects):
            filtered_objects.append(detected_obj)

            class_id = detected_obj["class_id"]
            obj_name = detected_obj["name"]

            new_counts[class_id]["name"] = obj_name
            new_counts[class_id]["count"] += 1

    if new_counts != object_counts:
        print("\nObject count changed! Updating Firebase...")

        db.child(username).child(dataset).remove()
        for i, detected_obj in enumerate(filtered_objects):
            unique_key = f"{i}-{detected_obj['class_id']}"
            db.child(username).child(dataset).child(unique_key).set(detected_obj)

        db.child(username).child(count_dataset).set(new_counts)

        print("Updated Object Counts:")
        for class_id, data in new_counts.items():
            print(f"{data['name']} (ID {class_id}): {data['count']}")

        object_counts = new_counts.copy()

    time.sleep(2)

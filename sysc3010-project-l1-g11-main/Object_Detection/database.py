import pyrebase
import time
from collections import defaultdict
from detect import Detect

# Initialize object detection
obj = Detect()

# Firebase configuration
config = {
    "apiKey": "AIzaSyCxXKQE9ietlYXU9Sm5qzXLb27G1xR0prs", 
    "authDomain": "lab3-8f22c.firebaseapp.com", 
    "databaseURL": "https://lab3-8f22c-default-rtdb.firebaseio.com/", 
    "storageBucket": "lab3-8f22c.appspot.com"
}

# Connect to Firebase
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

# Function to check if an object is already counted (avoiding duplicates)
def is_new_object(detected_obj, existing_objects, threshold=50):
    """
    Checks if the detected object is new or an existing one.
    
    Arguments:
    - detected_obj: Object being detected
    - existing_objects: Dictionary of already counted objects
    - threshold: Distance threshold to consider the object the same
    
    Returns:
    - True if it's a new object, False if it's a duplicate
    """
    class_id = detected_obj["class_id"]
    bbox = detected_obj["bounding_box"]

    for existing_obj in existing_objects:
        if existing_obj["class_id"] == class_id:
            # Compute distance between bounding box centers
            x1 = bbox["left"] + (bbox["right"] - bbox["left"]) / 2
            y1 = bbox["top"] + (bbox["bottom"] - bbox["top"]) / 2
            
            existing_bbox = existing_obj["bounding_box"]
            x2 = existing_bbox["left"] + (existing_bbox["right"] - existing_bbox["left"]) / 2
            y2 = existing_bbox["top"] + (existing_bbox["bottom"] - existing_bbox["top"]) / 2

            distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5  # Euclidean distance
            
            if distance < threshold:
                return False  # Object is too close ? likely a duplicate

    return True  # Object is new

# Real-time detection loop
while True:
    detected_objects = obj.detect_obj()  # Get detected objects
    new_counts = defaultdict(lambda: {"name": "", "count": 0})
    filtered_objects = []  # List to store non-duplicate objects

    # Process new detections (filter out duplicates)
    for detected_obj in detected_objects:
        if is_new_object(detected_obj, filtered_objects):
            filtered_objects.append(detected_obj)

            class_id = detected_obj["class_id"]  # Object class ID
            obj_name = detected_obj["name"]  # Object name

            # Update new counts dictionary
            new_counts[class_id]["name"] = obj_name
            new_counts[class_id]["count"] += 1

    # Check if counts have changed (added/removed objects)
    if new_counts != object_counts:
        print("\n? Object count changed! Updating Firebase...")
        
        # Upload new detection data
        db.child(username).child(dataset).remove()  # Clear old detection dataset
        for i, detected_obj in enumerate(filtered_objects):
            unique_key = f"{i}-{detected_obj['class_id']}"
            db.child(username).child(dataset).child(unique_key).set(detected_obj)

        # Upload updated object counts
        db.child(username).child(count_dataset).set(new_counts)

        # Print updated counts
        print("? Updated Object Counts:")
        for class_id, data in new_counts.items():
            print(f"{data['name']} (ID {class_id}): {data['count']}")

        # Update the local tracking dictionary
        object_counts = new_counts.copy()

    time.sleep(2)  # Prevent excessive Firebase writes (adjust as needed)

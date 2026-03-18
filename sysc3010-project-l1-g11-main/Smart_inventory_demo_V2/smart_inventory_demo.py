import paho.mqtt.client as mqtt
import json
import time
import requests
import sqlite3
import random

# MQTT Configuration
BROKER_ADDRESS = "172.17.176.209"  # Replace with RPi 2's IP
TOPIC = "test/run"

# Test Data
TEST_ITEM = {
    "id": random.randint(1000, 9999),
    "name": "Milk",
    "quantity": 2,
    "expiration_date": "2025-06-30"
}

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(TOPIC)  # Listen for test commands

def on_message(client, userdata, msg):
    """Runs the assigned test when an MQTT message is received."""
    command = msg.payload.decode()
    print(f" Received test command: {command}")

    if command == "camera_to_ai" and DEVICE_ROLE == "RPi_2":
        test_camera_to_ai()
    elif command == "gui_database" and DEVICE_ROLE == "RPi_1":
        test_gui_database()
    elif command == "inter_device_mqtt" and DEVICE_ROLE == "RPi_3":
        test_inter_device_mqtt()
    elif command == "database" and DEVICE_ROLE == "RPi_4":
        test_database()

#  Modify DEVICE_ROLE for each Raspberry Pi Adel:RPi_1 ; Agrim: RPi_2; Kumud: RPi_3; Raph: RPi_4
DEVICE_ROLE = "RPi_X"  # Replace with RPi_1, RPi_2, RPi_3, or RPi_4

# Define each test function
def test_camera_to_ai():
    print("[Agrim] Testing Camera Node Communication...")
    client = mqtt.Client()
    client.connect(BROKER_ADDRESS, 1883, 60)
    message = json.dumps({"camera_id": "RPi-3", "image": "image_data_here"})
    client.publish("camera/input", message)
    print("📤 Image data sent to AI Processing Server.")
    time.sleep(2)
    client.disconnect()

def test_gui_database():
    print("[Adel] Testing GUI to Database Communication...")
    response = requests.post(f"http://{BROKER_ADDRESS}:5000/add_item", json=TEST_ITEM)
    if response.status_code == 200:
        print(" Item successfully added to database.")
    else:
        print(" Database update failed.")

def test_inter_device_mqtt():
    print("[Kumud] Testing Inter-Device Communication...")
    client = mqtt.Client()
    client.connect(BROKER_ADDRESS, 1883, 60)
    test_message = json.dumps({"from": "RPi-1", "to": "RPi-2", "action": "Request Item List"})
    client.publish("system/requests", test_message)
    print(" Sent item list request.")
    time.sleep(2)
    client.disconnect()

def test_database():
    print("[Raphael] Testing Database Operations...")
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS inventory (id INTEGER, name TEXT, quantity INTEGER, expiration TEXT)")
    cursor.execute("INSERT INTO inventory VALUES (?, ?, ?, ?)", (TEST_ITEM["id"], TEST_ITEM["name"], TEST_ITEM["quantity"], TEST_ITEM["expiration_date"]))
    conn.commit()
    cursor.execute("SELECT * FROM inventory")
    results = cursor.fetchall()
    print("Database contents:", results)
    conn.close()

# Start MQTT listener
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_ADDRESS, 1883, 60)
client.loop_forever()

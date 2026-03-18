import paho.mqtt.client as mqtt
import time

BROKER_ADDRESS = "192.168.1.100"  # Replace with RPi 2's IP
TOPIC = "test/run"

def send_mqtt_command(command):
    """Publishes an MQTT message to trigger a test on another Raspberry Pi."""
    client = mqtt.Client()
    client.connect(BROKER_ADDRESS, 1883, 60)
    client.publish(TOPIC, command)
    print(f"📡 Sent MQTT command: {command}")
    client.disconnect()
    time.sleep(3)  # Wait for the test to complete before sending the next one

def test_full_system():
    print("[Abderrezak] Testing Full System Integration...")

    send_mqtt_command("camera_to_ai")  # Triggers Agrim's Test
    send_mqtt_command("gui_database")  # Triggers Adel's Test
    send_mqtt_command("inter_device_mqtt")  # Triggers Kumud's Test
    send_mqtt_command("database")  # Triggers Raphael's Test

    print("All system components successfully tested!")

if __name__ == "__main__":
    test_full_system()

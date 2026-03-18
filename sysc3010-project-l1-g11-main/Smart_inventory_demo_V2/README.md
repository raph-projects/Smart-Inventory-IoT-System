# Smart Inventory Demo

## Project Overview
This project demonstrates an end-to-end communication system for a Smart Inventory System using:
- MQTT for inter-device messaging
- Flask API for GUI and database interaction
- SQLite Database for inventory storage

Each Raspberry Pi is assigned a specific role in the system.

## Raspberry Pi Assignments
| Raspberry Pi | Team Member | Function |
|-------------|------------|----------|
| RPi 1       | Adel       | Runs Flask API & listens for GUI test commands |
| RPi 2       | Agrim      | Runs MQTT Broker & listens for Camera to AI test commands |
| RPi 3       | Kumud      | Listens for Inter-Device MQTT test commands |
| RPi 4       | Raphael    | Listens for Database test commands |
| RPi 5       | Zak        | Triggers all tests via MQTT |

## Setup Instructions

### 1. Clone the Repository
On each Raspberry Pi, run:
```bash
git clone https://github.com/yourusername/Smart_Inventory_Demo.git
cd Smart_Inventory_Demo
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Find RPi 2’s IP Address (For MQTT Broker)
On **RPi 2 (Agrim's device)**, run:
```bash
hostname -I
```
- Note the IP address (e.g., `192.168.1.100`).
- Agrim should share this IP with the team.

### 4. Update the Broker Address in All Scripts
Each team member should update `BROKER_ADDRESS` in `smart_inventory_demo.py` and `test_full_system.py`:
```python
BROKER_ADDRESS = "192.168.1.100"  # Replace with the actual RPi 2 IP
```

### 5. Verify RPi 2 Is Reachable From Other Raspberry Pis
Each team member should test the connection to RPi 2 by running:
```bash
ping 192.168.1.100
```
If the ping fails:
1. Ensure RPi 2 is powered on and connected to the network.
2. Ensure all Raspberry Pis are on the same WiFi network.
3. Check RPi 2’s firewall settings:
   ```bash
   sudo ufw allow 1883
   ```

### 6. Start MQTT Broker on Raspberry Pi 2 (Agrim)
On **RPi 2**, run:
```bash
sudo systemctl start mosquitto
sudo systemctl enable mosquitto  # Ensures the broker starts on boot
```
Check if it is running:
```bash
sudo systemctl status mosquitto
```
If working, you should see:
```
● mosquitto.service - Mosquitto MQTT Broker
   Loaded: loaded (/lib/systemd/system/mosquitto.service; enabled)
   Active: active (running)
```

### 7. Start Flask API on Raspberry Pi 1 (Adel)
```bash
python3 server.py
```
This must be running before other tests.

### 8. Update the Device Role on Each Raspberry Pi
Each Raspberry Pi should modify `smart_inventory_demo.py` by setting the correct role:
```python
DEVICE_ROLE = "RPi_X"  # Replace with RPi_1, RPi_2, RPi_3, or RPi_4
```

### 9. Start the MQTT Listener on Each Raspberry Pi (RPi 1, 2, 3, 4)
On **RPi 1, RPi 2, RPi 3, and RPi 4**, run:
```bash
python3 smart_inventory_demo.py
```
Each Raspberry Pi will now wait for Zak’s MQTT command before running its test.

### 10. Run the Full System Test from Raspberry Pi 5 (Zak)
On **RPi 5 (Zak)**, run:
```bash
python3 test_full_system.py
```
Zak’s script will send MQTT messages to each Raspberry Pi, and those Raspberry Pis will run their assigned test.

## Expected Demo Results
| Test | Expected Output |
|------|----------------|
| Run `test_camera_to_ai()` | `Sent test image from RPi-3 to AI Processing Server.` |
| Run `test_gui_database()` | `Item successfully added to database.` |
| Run `test_inter_device_mqtt()` | `Sent item list request.` |
| Run `test_database()` | `Database contents: [(ID, 'Milk', 2, '2025-06-30')]` |
| Run `test_full_system()` | `All system components successfully tested.` |

## MQTT Debugging

### Check if the MQTT Broker is Running
```bash
sudo systemctl status mosquitto
```
If it is not running, start it:
```bash
sudo systemctl start mosquitto
```

### Listen for MQTT Messages (Debug Mode)
Each team member (except Zak) should run:
```bash
mosquitto_sub -h 192.168.1.100 -t "#" -v
```
This will show all incoming MQTT messages.

### Manually Send an MQTT Test Message
```bash
mosquitto_pub -h 192.168.1.100 -t "test/run" -m "gui_database"
```
If no message appears in `mosquitto_sub`, MQTT is not working.

## Database Debugging

### 1. Check if Inventory Database Exists
```bash
ls -l inventory.db
```
If the database is missing, run:
```bash
python3 server.py
```

### 2. View Stored Inventory Data
```bash
sqlite3 inventory.db "SELECT * FROM inventory;"
```

## Flask API Debugging

### 1. Check if Flask is Running
```bash
sudo netstat -tulnp | grep 5000
```
If nothing appears, restart Flask:
```bash
python3 server.py
```

### 2. Manually Test Adding an Item to the Database
```bash
curl -X POST http://127.0.0.1:5000/add_item -H "Content-Type: application/json" -d '{"id":101, "name":"Milk", "quantity":2, "expiration_date":"2025-06-30"}'
```

### 3. Retrieve Inventory Data
```bash
curl -X GET http://127.0.0.1:5000/get_inventory
```

## Troubleshooting Common Issues
| Issue | Solution |
|-------|----------|
| MQTT messages not being received? | Run `mosquitto_sub -h 192.168.1.100 -t "#" -v` to listen for messages. |
| Flask API is not responding? | Restart it: `python3 server.py`. |
| Database is empty? | Check inventory manually: `sqlite3 inventory.db "SELECT * FROM inventory;"`. |
| Devices not communicating? | Ensure all Raspberry Pis are on the same network. |

---

# Ultrasonic Sensor Module – Smart Inventory System

This folder contains the standalone implementation for the **Ultrasonic Sensor Node (RPi-5)** in the Smart Inventory System. The ultrasonic sensor monitors the distance (i.e., fill level) of a container or shelf and triggers alerts when inventory is running low. This node runs independently and communicates with Firebase for real-time updates.

---

## 📌 Features

- Periodic distance measurement using **HC-SR04 ultrasonic sensor**
- Alerts sent to Firebase when item level is low
- Modular, testable codebase
- Designed to run within a virtual environment (`venv`) on Raspberry Pi

---

## 📁 Folder Structure

- `ultrasonic.py`  
  ↳ Main script to run the ultrasonic sensor

- `test_sensor_module.py`  
  ↳ Test script for the ultrasonic sensor module

- `test_server.py`  
  ↳ Script to test Firebase interaction (mock/local)

- `database/`  
  ├─ `db.json`  
  │   ↳ Local mock database used for testing  
  └─ `README.md`  
      ↳ Notes describing the mock DB structure

- `README.md`  
  ↳ This documentation file

---

## 🧰 Hardware Required

- Raspberry Pi (with GPIO support)
- HC-SR04 Ultrasonic Sensor
- Jumper wires
- Breadboard

### ⚙️ Wiring Example

| HC-SR04 Pin | Raspberry Pi GPIO |
|-------------|-------------------|
| VCC         | 5V                |
| GND         | GND               |
| TRIG        | GPIO 23           |
| ECHO        | GPIO 16           |

> You can modify the pin configuration in `ultrasonic.py` if needed.

---

## 🧪 Prerequisites

- Python 3.x installed
- Virtual environment (`venv`) setup
- Firebase project with database access and credentials
- Internet access on Raspberry Pi (for Firebase sync)

---

## 🚀 Setup & Execution

### 1. Navigate to the project folder:

```bash
cd Ultrasonic_Sensor
```

### 2. Activate the virtual environment:
```bash
source bin/venv/activate
```

### 3. Install dependencies (if needed):
```bash
pip install -r requirements.txt
```

### 4. Add your Firebase configuration file:
```bash
python3 ultrasonic.py
```
---
## 🧪 Testing
Use the provided test scripts to validate the setup:
- **test_sensor_module.py** – Test ultrasonic readings
- **test_server.py** – Simulate database/Firebase interaction

---

## 📬 Output Behaviour
- Sensor measures distance in centimeters.
- If the distance exceeds the threshold (i.e., low stock), it logs/sends an alert.
- Distance values and statuses are printed to the console and/or sent to Firebase.

---

## 🧑‍💻 Author
This module was developed as part of the Smart Inventory System for SYSC 3010 – Real-Time Concurrent Systems Design.

**By: Abderrezak Foura**


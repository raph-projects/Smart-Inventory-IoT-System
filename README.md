# Smart Pantry Inventory System

An AI-powered, IoT-based smart inventory system built on a distributed network of five Raspberry Pi nodes. The system automatically tracks pantry items in real time using computer vision, weight sensing, ultrasonic detection, and a Firebase backend — eliminating the need for manual inventory management.

> **Course:** SYSC 3010 — Computer Systems Development Project | Carleton University

---

## Overview

Managing a home pantry is a persistent challenge — food expires, items run out unexpectedly, and manual tracking is error-prone. This project automates pantry management by combining AI-based image recognition, IoT hardware, and real-time Firebase synchronization across a five-node Raspberry Pi network.

![image alt](https://github.com/raph-projects/Smart-Inventory-IoT-System/blob/80820ae9f425bfc0a54eb831254c1d741ed1403a/Pi-Stock_Final-product-picture.png)

**Key features:**
- **Automatic item detection** via EfficientDet Lite (TensorFlow Lite) object recognition
- **Weight-based item counting** using an HX711 load cell — tracks items like cutlery by weight delta
- **Ultrasonic sensing** to detect item placement and removal
- **Real-time Firebase backend** syncing all nodes instantly
- **LCD display + buzzer** for live inventory counts and low-stock alerts
- **HTML/JS GUI** reading live Firebase data and streaming camera feed via Flask
- **Multi-threaded peripheral controller** with backup inventory checker
- **Unit tested** — all major modules have corresponding test files

---

## 🏗️ System Architecture

The system is structured as a **distributed real-time network** of five Raspberry Pi nodes:

![image alt](https://github.com/raph-projects/Smart-Inventory-IoT-System/blob/477400fe12b7de76603d118e6f18c2fca378077e/Pi-Stock_Design%20Diagram.png)

---

### Communication Overview

| Link | Protocol | Purpose |
|------|----------|---------|
| All nodes ↔ Firebase | pyrebase (HTTPS) | Real-time data sync |
| RPi-1 ↔ SQLite | SQL | Local inventory storage and Flask API |
| RPi-2 → Firebase | pyrebase push | Object detection counts |
| RPi-5 → Firebase | pyrebase push | Weight delta + ultrasonic distance |
| RPi-4 ← Firebase | pyrebase stream | Triggers LCD and buzzer |
| RPi-3 → Flask | HTTP | Live camera feed to GUI |
| RPi-5 → RPi-4 | Firebase (indirect) | Ultrasonic triggers peripheral alerts |

---

## 📁 Project Structure

```
smart-pantry-inventory-system/
│
├── README.md
├── mydbconfig.example.py        ← Copy to mydbconfig.py and fill in credentials
│
├── Smart_inventory_demo_V2/     ← Full integration demo
│   ├── backend.py               ← Firebase backend class (user, device, camera)
│   ├── frontend.py              ← Dash/Flask live camera feed GUI
│   ├── authorize.py             ← Register authorized users on Firebase
│   ├── device.py                ← SenseHat LED stream handler
│   ├── server.py                ← Flask REST API with SQLite
│   ├── smart_inventory_demo.py  ← MQTT-based inter-device test runner
│   ├── test_full_system.py      ← Full system MQTT test orchestrator
│   ├── install.sh               ← Dependency installer
│   └── requirements.txt
│
├── Object_Detection/            ← RPi-2: AI object detection
│   ├── detect.py                ← EfficientDet Lite inference via TFLite
│   ├── database.py              ← Deduplication logic + Firebase sync
│   ├── utils.py                 ← Bounding box visualization (TF Apache 2.0)
│   └── efficientdet_lite0.tflite
│
├── Scale_Raph/                  ← RPi-5: HX711 load cell weight tracking
│   ├── loadcell.py              ← Calibration, item detection, Firebase sync
│   ├── weight_test.py           ← Live weight display for calibration
│   ├── test_scale.py            ← Unit tests for calibration and counting
│   └── server.py
│
├── Ultrasonic_Sensor/           ← RPi-5: HC-SR04 distance sensing
│   ├── ultrasonic.py            ← Distance measurement + Firebase sync
│   ├── test_sensor_module.py    ← Unit tests (mocked GPIO + time)
│   ├── test_server.py           ← Flask/TinyDB integration tests
│   └── database/
│       └── db.json              ← Local mock database for testing
│
├── Notifications/               ← RPi-4: LCD + buzzer peripheral controller
│   ├── inventory_monitor.py     ← 3-thread monitor (display / backup / ultrasonic)
│   ├── buzzer_test.py           ← Buzzer PWM test script
│   ├── test_display.py          ← LCD I2C display test
│   └── test_lowstock.py        ← Low stock alert simulation test
│
├── GUI/                         ← RPi-1: Web frontend
│   ├── index.html               ← Firebase live inventory table + camera feed
│   └── index_updated.html       ← Improved combined data rendering
│
└── Database/                    ← RPi-1: Flask API + local DB
    ├── server.py                ← REST API: /add_item, /get_inventory
    ├── mydb_script.py           ← TinyDB setup script
    └── db.json                  ← Local mock database
```

---

## ⚙️ Setup & Requirements

### Hardware
- 5× Raspberry Pi (3B+ or 4)
- Raspberry Pi Camera Module v2
- USB Webcam (for RPi-2 secondary feed)
- HC-SR04 Ultrasonic Sensor
- HX711 Load Cell Amplifier + Load Cell
- 16×2 I2C LCD Display (PCF8574 at `0x27`)
- Active Piezo Buzzer

### Wiring Reference

**Ultrasonic Sensor (HC-SR04):**
| Pin | GPIO |
|-----|------|
| TRIG | GPIO 23 |
| ECHO | GPIO 16 |

**Load Cell (HX711):**
| Pin | GPIO |
|-----|------|
| DOUT | GPIO 6 |
| SCK | GPIO 5 |

**LCD Display (I2C):**
| Pin | GPIO |
|-----|------|
| SDA | GPIO 2 (Pin 3) |
| SCL | GPIO 3 (Pin 5) |

**Buzzer:**
| Pin | GPIO |
|-----|------|
| IN | GPIO 16 (PWM) |

### Software Dependencies

```bash
# All nodes
pip install pyrebase4 coloredlogs

# RPi-2 (AI)
pip install tflite-support opencv-python picamera2

# RPi-4 (Notifications)
pip install RPLCD smbus2 RPi.GPIO

# RPi-5 (Scale)
pip install hx711py RPi.GPIO

# RPi-5 (Ultrasonic)
pip install RPi.GPIO

# RPi-1 (Database/GUI)
pip install flask tinydb

# RPi-3 (Camera GUI)
pip install dash flask picamera2 opencv-python
```

Or use the provided installer:
```bash
bash Smart_inventory_demo_V2/install.sh
```

### Firebase Configuration

Copy the example config and fill in your own Firebase credentials:
```bash
cp mydbconfig.example.py mydbconfig.py
```


Enable I2C on Raspberry Pi (for LCD):
```bash
sudo raspi-config  # Interface Options > I2C > Enable
sudo reboot
```

Verify LCD is detected:
```bash
i2cdetect -y 1  # Should show 0x27
```

---

## 🚀 Running the System

Start each node in this order:

**RPi-2 — AI Object Detection:**
```bash
cd Object_Detection
python3 database.py
```

**RPi-5 — Scale:**
```bash
cd Scale_Raph
python3 loadcell.py
```

**RPi-5 — Ultrasonic Sensor:**
```bash
cd Ultrasonic_Sensor
python3 ultrasonic.py
```

**RPi-4 — Peripheral Controller (LCD + Buzzer):**
```bash
cd Notifications
python3 inventory_monitor.py
```

**RPi-1 — Flask API:**
```bash
cd Database
python3 server.py
```

**RPi-1 — GUI (open in browser):**
```bash
cd GUI
python3 -m http.server 8000
# Visit http://<RPi-1-IP>:8000
```

---

## 🔍 How It Works

**Automatic Item Detection (Camera):**
1. Picamera2 or USB webcam captures frames continuously on RPi-2
2. EfficientDet Lite model identifies objects with confidence > 30%
3. Deduplication logic filters out duplicate bounding boxes using Euclidean distance
4. Object names and counts are pushed to Firebase under `agrim/Object_Count`
5. GUI reads Firebase in real time and updates the inventory table

**Weight-Based Item Tracking (Scale):**
1. HX711 load cell measures weight delta on the scale platform
2. Delta is matched against calibrated per-item weights (±3g tolerance)
3. Item counts are incremented/decremented and pushed to Firebase under `raphael/Smart_Scale_Simple`
4. Scale auto-resets all counts to 0 when the platform is empty

**Peripheral Alerts (LCD + Buzzer):**
1. `inventory_monitor.py` runs three threads simultaneously:
   - **Display thread:** scrolls through all items on the LCD every 2 seconds
   - **Ultrasonic thread:** watches Firebase for new distance readings; if `< 45cm`, pauses display and shows add/remove alert
   - **Backup thread:** polls Firebase every 5 seconds as a fallback detector
2. Buzzer beeps on item add (short), remove (medium), or low stock (rapid)

---

## 🧪 Testing

Each module has a dedicated test file:

| File | What it tests |
|------|--------------|
| `test_scale.py` | Calibration ratio calculation, object counting logic |
| `test_sensor_module.py` | Ultrasonic distance measurement (mocked GPIO) |
| `test_server.py` | Flask API object detection and TinyDB storage |
| `test_display.py` | LCD I2C write |
| `test_lowstock.py` | Low stock buzzer and LCD alert simulation |
| `test_full_system.py` | Full MQTT-based end-to-end test orchestration |

Run unit tests:
```bash
python3 -m unittest test_scale.py
python3 -m unittest test_sensor_module.py
```

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![TensorFlow](https://img.shields.io/badge/AI-TFLite%20EfficientDet-orange?logo=tensorflow)
![OpenCV](https://img.shields.io/badge/Vision-OpenCV-green)
![Firebase](https://img.shields.io/badge/Backend-Firebase-yellow?logo=firebase)
![Flask](https://img.shields.io/badge/API-Flask-lightgrey?logo=flask)
![MQTT](https://img.shields.io/badge/IoT-MQTT-purple)
![RaspberryPi](https://img.shields.io/badge/Hardware-Raspberry%20Pi-C51A4A?logo=raspberrypi)

---

## 👥 Team — Group L1-G11

| Name | Node | Key Contributions |
|------|------|------------------|
| Agrim Kasaju | RPi-2 | AI object detection, Firebase sync, camera GUI |
| Adel Jaber | RPi-1 | Flask API, SQLite database, GUI frontend |
| Kumud Bansal | RPi-3 | Camera node, MQTT inter-device communication |
| Abderrezak Foura | RPi-5 | Ultrasonic sensor module, Firebase distance alerts |
| Raphael Dube | RPi-4/5 | Load cell scale, peripheral controller (LCD/buzzer), unit tests |

---

## 📄 License

Built for academic purposes at Carleton University. Architecture and design are free to reference — please don't submit as your own coursework.

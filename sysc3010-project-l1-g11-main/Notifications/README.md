# Inventory Monitoring System - README

##  Project Overview
This project is an **Inventory Monitoring System** using:
- **I2C LCD Display** to show item updates.
- **Buzzer** for notifications (item added/removed, low stock).
- **SQLite Database** (or MySQL) to store inventory data.
- **Raspberry Pi 4** as the main controller.

---

##  1. Hardware Requirements
✔ Raspberry Pi 4 (or any Pi with I2C support)  
✔ I2C LCD Display (16x2 or 20x4, PCF8574 driver)  
✔ Passive or Active Buzzer (low-level trigger)  
✔ Breadboard & Jumper Wires  
✔ Resistors (Optional: 330Ω to 1KΩ for buzzer)  
✔ Power Supply for Raspberry Pi  

---

##  2. Software Requirements
### **Install Required Libraries**
Run the following commands to install dependencies:
```bash
sudo apt update
sudo apt install sqlite3 python3-pip
pip install smbus2 RPLCD RPi.GPIO
```

### **Enable I2C on Raspberry Pi**
```bash
sudo raspi-config
```
- Navigate to **Interface Options > I2C** and enable it.
- Reboot the Raspberry Pi:
  ```bash
  sudo reboot
  ```

---

##  3. Setting Up the Test Database
### **Create and Populate a Test SQLite Database**
Run the following to create `inventory.db`:
```bash
sqlite3 inventory.db
```
Inside the SQLite shell, run:
```sql
CREATE TABLE inventory (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    threshold INTEGER NOT NULL
);

INSERT INTO inventory (item_name, quantity, threshold) VALUES ('Milk', 5, 2);
INSERT INTO inventory (item_name, quantity, threshold) VALUES ('Bread', 1, 3);
INSERT INTO inventory (item_name, quantity, threshold) VALUES ('Eggs', 12, 5);
.exit
```
To verify:
```bash
sqlite3 inventory.db "SELECT * FROM inventory;"
```

---

##  4. Wiring the Components
### **LCD Wiring (I2C SDA/SCL)**
| LCD Pin | Raspberry Pi Pin |
|---------|------------------|
| VCC     | 5V (Pin 2 or 4)  |
| GND     | GND (Pin 6, 9)   |
| SDA     | GPIO2 (Pin 3)    |
| SCL     | GPIO3 (Pin 5)    |

### **Buzzer Wiring (PWM-Controlled)**
| Buzzer Pin | Raspberry Pi Pin |
|-----------|------------------|
| VCC       | 5V (Pin 2 or 4)  |
| GND       | GND (Pin 6, 9)   |
| IN        | GPIO16 (Pin 36)  |

---

## 5. Running the Code
### **Run the Inventory Monitor Script**
Save the Python script as `inventory_monitor.py` and run:
```bash
python3 inventory_monitor.py
```

### **Simulating Item Changes for Testing**
To **add an item**:
```bash
sqlite3 inventory.db "UPDATE inventory SET quantity = quantity + 1 WHERE item_name = 'Milk';"
```
To **remove an item**:
```bash
sqlite3 inventory.db "UPDATE inventory SET quantity = quantity - 1 WHERE item_name = 'Bread';"
```
To **simulate low stock**:
```bash
sqlite3 inventory.db "UPDATE inventory SET quantity = 1 WHERE item_name = 'Eggs';"
```

Expected **LCD Display & Buzzer Behavior**:
- **Item Added:** "Added: [Item]" (Quick Beep )
- **Item Removed:** "Removed: [Item]" (Slightly Longer Beep )
- **Low Stock Alert:** "LOW STOCK: [Item]" (Rapid Beeping )

---

##  6. Testing and Debugging
### **Checking I2C Device Address**
Run:
```bash
i2cdetect -y 1
```
Expected output (LCD should be detected at `0x3F` or `0x27`):
```
     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- 27 -- -- -- -- -- -- --
```
If LCD is **not detected**, check the wiring.

### **Checking the Buzzer**
Run a manual buzzer test:
```python
import RPi.GPIO as GPIO
import time

BUZZER_PIN = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)
time.sleep(1)
GPIO.output(BUZZER_PIN, GPIO.HIGH)
GPIO.cleanup()
```
If no sound, check wiring and power.

---

##  7. GitHub & Demo Readiness
### **Push Code to GitHub**
Ensure all files are committed before the demo:
```bash
git add .
git commit -m "Added inventory monitoring system"
git push origin main
```

### **Unit Test Readiness Checklist**
✅ All required scripts (`inventory_monitor.py`, `test_buzzer.py`, etc.) are present.  
✅ Database setup instructions are clear and verified.  
✅ Hardware connections are tested and functional.  
✅ Git repository is up to date.  
✅ Team is prepared to **demonstrate real-time item tracking**.  

---

##  8. Future Improvements
- **Integrate with MySQL** for multi-device access.
- **Add real-time notifications** via MQTT or Web API.
- **Optimize LCD refresh** for better performance.

---

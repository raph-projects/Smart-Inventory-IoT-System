import sqlite3
import time
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2)

BUZZER_PIN = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

pwm = GPIO.PWM(BUZZER_PIN, 2000)  # 2kHz frequency

conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Simulate low stock
cursor.execute("UPDATE inventory SET quantity = 1 WHERE item_name = 'Eggs';")
conn.commit()

cursor.execute("SELECT item_name, quantity, threshold FROM inventory WHERE quantity < threshold;")
low_stock_items = cursor.fetchall()
conn.close()

if low_stock_items:
    lcd.clear()
    lcd.write_string(f"LOW STOCK:\n{low_stock_items[0][0]}")
    pwm.start(50)
    time.sleep(1)
    pwm.stop()
    time.sleep(1)
    pwm.start(50)
    time.sleep(1)
    pwm.stop()
    lcd.clear()

GPIO.cleanup()

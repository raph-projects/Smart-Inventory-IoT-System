import smbus2
import time
from RPLCD.i2c import CharLCD


# Set LCD addresses
lcd1_address = 0x27  # Change if different

# Initialize both LCDs
lcd1 = CharLCD(i2c_expander='PCF8574', address=lcd1_address, port=1, cols=16, rows=2)

# Display messages
lcd1.clear()
lcd1.write_string("this is a test   :)")

time.sleep(10)

# Clear screens
lcd1.clear()





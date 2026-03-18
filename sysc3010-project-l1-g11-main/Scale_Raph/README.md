# 📦 Smart Scale — Simple Version

```
A Raspberry Pi-based smart scale system that uses a load cell (HX711) to detect and count specific items placed on or removed from the scale. This version supports one-time calibration per item and syncs live data to Firebase.

🛠 Features
- Zeroes the scale before use  
- Calibrates with a known weight  
- One-time calibration for unique items  
- Detects when items are added or removed  
- Matches weight changes to known items  
- Live updates item counts to Firebase  
- Automatically resets if the scale is emptied

🧰 Hardware Requirements
- Raspberry Pi (any model with GPIO)  
- HX711 Load Cell Amplifier  
- Load Cell sensor  
- Jumper wires  
- Stable platform or scale base

🔧 Software Setup

1. Install Dependencies

    pip install RPi.GPIO hx711py pyrebase4

    Note: hx711py is the HX711 Python library. If it doesn't install directly, you may need to install from source:
    https://github.com/tatobari/hx711py

2. Clone the Repository

    git clone https://github.com/yourusername/smart-scale-simple.git
    cd smart-scale-simple

3. Configure Firebase

    Update the config dictionary in the code with your own Firebase credentials:

    config = {
        "apiKey": "...",
        "authDomain": "...",
        "databaseURL": "...",
        "storageBucket": "..."
    }

🚀 How to Use

Step-by-step:

1. Run the script:

    python smart_scale.py

2. Zero the scale  
   Remove all items and press Enter.

3. Calibrate using a known weight  
   Place a known object on the scale, enter its weight in grams.

4. Calibrate unique items  
   You'll be prompted to enter the name and weight of each item once.

5. Live Detection Starts  
   The system will detect when items are added or removed and update Firebase accordingly.

🔄 Firebase Structure

root/
└── username/
    └── Smart_Scale_Simple/
        ├── item1: count
        ├── item2: count
        └── ...

📏 Tolerance Settings

- Default tolerance: ±3 grams  
- Ignores fluctuations under 2 grams  
- Resets counts if total weight is close to 0 grams

🧠 Detection Logic

The algorithm:
- Measures the weight difference (delta)  
- Checks which calibrated item closely matches delta within tolerance  
- Estimates count based on item weight  
- Updates item counts and Firebase

🛑 Exit

To safely exit:
- Press Ctrl + C  
- GPIO pins are automatically cleaned up

📄 License

MIT License  
Feel free to use, modify, and share!

👤 Author

Raphael Dubé  
Smart Scale — Simplified Counting System
```

# Smart Inventory System

This repository contains the source code and documentation for the Smart Inventory System, a distributed real-time inventory monitoring solution designed using Raspberry Pi devices, AI-based object detection, and a Firebase backend. The system streamlines home or industrial inventory management by automating the tracking, updating, and notification processes for stored items.

## Table of Contents

- [Project Description](#project-description)
- [System Architecture](#system-architecture)
- [Hardware Components](#hardware-components)
- [Software Components](#software-components)
- [Getting Started](#getting-started)
- [Running the System](#running-the-system)
- [Repository Structure](#repository-structure)
- [Testing](#testing)
- [Contributors](#contributors)

## Project Description

The Smart Inventory System (PiStock) addresses common inventory management issues such as redundant purchases and expired goods. It uses image recognition and IoT technology to identify, track, and manage items in real-time, reducing human error and improving accuracy.

Key features:
- Real-time inventory updates
- AI-powered object recognition
- Low-stock and expiration alerts
- Firebase-based cloud storage
- LCD, buzzer, and ultrasonic sensor feedback for user notifications


## System Architecture

The system consists of four interconnected Raspberry Pi nodes:

- **RPi-1 (User Interface & Database):** Hosts the GUI and syncs with Firebase.
- **RPi-2 (AI Processing Server):** Runs object detection using TensorFlow Lite.
- **RPi-3 (Camera Node):** Captures images of inventory items.
- **RPi-4 (Peripheral Controller):** Manages the LCD display and buzzer for real-time feedback.
- **RPi-5 (Ultrasonic Sensor Node):** Implements a standalone ultrasonic sensor module that measures distance to detect fill levels and alerts Firebase when a low-stock threshold is reached.

Each storage unit is identified by a unique 'inventory_ID', supporting scalability across different environments (e.g., fridge, pantry, warehouse).


## Hardware Components

- 5× Raspberry Pi boards
- Raspberry Pi Camera Module
- Ultrasonic Sensor (e.g., HC-SR04)
- 16x2 I2C LCD Display
- Buzzer
- Digital Scale for weight-based quantity estimation

## Software Components

- Python 3.x
- TensorFlow Lite
- Firebase Realtime Database
- Flask (for REST API communication)
- PiCamera / Picamera2
- RPi.GPIO or gpiozero
- HTML/CSS for GUI frontend

## Getting Started

### Prerequisites

- Python 3.x installed on all Raspberry Pi devices
- Internet connection for Firebase integration
- Firebase project with authentication and database rules configured

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/CU-SYSC3010W25/sysc3010-project-l1-g11
    cd sysc3010-project-l1-g11
    ```

2. Install dependencies (repeat on each Raspberry Pi node as needed):
    ```bash
    pip install -r requirements.txt
    ```

3. Configure Firebase credentials:
    - Create a `firebase_config.json` file in the root directory.
    - Populate it with your Firebase Web SDK credentials.

## Running the System

Each Raspberry Pi runs a dedicated script:

- **RPi-1 (GUI & DB Sync):**
    ```bash
    python3 -m http.server 8000
    ```

- **RPi-2 (AI Detection & Firebase Sync):**
    ```bash
    cd Object_Detection
    python3 detect.py
    ```

- **RPi-3 (Scale):**
    ```bash
    cd Scale_Raph
    source bin/venv/activate
    python3 loadcell.py
    ```

- **RPi-4 (Peripheral Controls):**
    ```bash
    cd Notifications
    python3 inventory_monitor.py
    ```
- **RPi-5 (Ultrasonic Sensor):**
    ```bash
    cd Ultrasonic_Sensor
    source bin/venv/activate
    python3 ultrasonic.py
    ```

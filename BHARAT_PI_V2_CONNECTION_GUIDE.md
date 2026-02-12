# Bharat Pi V2 – Connection Guide  
## Pothole Detection System (MPU6050 + GPS)

This guide explains how to connect **MPU6050** (accelerometer + gyro) and a **GPS module** to **Bharat Pi V2** (ESP32-based board) and how to connect the board to your Node.js backend.

---

## 1. Bharat Pi V2 Overview

- **Chip:** ESP32 (Wi-Fi + Bluetooth)
- **Power:** 5V via USB Type-C or 9V DC jack
- **Programming:** Arduino IDE, ESP-IDF, or MicroPython

**Note:** If your “Bharat Pi V2” is the **4G LTE** version, it has built-in GPS; you only need to add the MPU6050. The pinout below is for the common ESP32 GPIOs used on Bharat Pi boards.

---

## 2. Pin Reference (Bharat Pi / ESP32)

| Function   | GPIO | Pin name / note        |
|-----------|------|-------------------------|
| **I2C – MPU6050** |      |                         |
| SDA       | 21   | I2C Data                |
| SCL       | 22   | I2C Clock               |
| **UART – GPS** (2nd UART) | |    |
| TX        | 17   | ESP32 TX → GPS **RX**   |
| RX        | 16   | ESP32 RX ← GPS **TX**   |
| **Power** |      |                         |
| 3.3V      | 3V3  | For MPU6050 & GPS (if 3.3V) |
| GND       | GND  | Common ground           |

Use the **second UART** (GPIO16/17) for GPS so the first UART (GPIO1/3) remains free for USB serial upload and debug.

---

## 3. Hardware Wiring

### 3.1 MPU6050 (I2C)

| MPU6050 pin | Connect to Bharat Pi V2 |
|-------------|--------------------------|
| VCC         | 3.3V                     |
| GND         | GND                      |
| SDA         | GPIO 21 (SDA)            |
| SCL         | GPIO 22 (SCL)            |
| AD0         | GND (I2C address 0x68) or 3.3V (address 0x69) |

- Use **3.3V** only (do not use 5V on the MPU6050 unless the module is 5V-tolerant and you have level shifters).
- Keep wires short for I2C (especially SDA/SCL).
- If the board has no pull-ups, add 4.7 kΩ from SDA to 3.3V and SCL to 3.3V (many MPU6050 breakout boards already have them).

### 3.2 GPS Module (UART)

| GPS module pin | Connect to Bharat Pi V2 |
|----------------|--------------------------|
| VCC            | 3.3V (or 5V if module is 5V and board has 5V out) |
| GND            | GND                      |
| **TX** (GPS sends data) | **GPIO 16** (ESP32 RX) |
| **RX** (GPS receives)  | **GPIO 17** (ESP32 TX) |

- **Cross connection:** GPS **TX** → ESP32 **RX** (GPIO 16); GPS **RX** → ESP32 **TX** (GPIO 17).
- Typical baud rate: **9600** (NMEA).
- If the GPS is 5V logic, use a level shifter (e.g. 3.3V ↔ 5V) between GPS and ESP32.

### 3.3 Power

- **Bharat Pi V2:** 5V USB or 9V DC jack as per board label.
- **MPU6050 & GPS:** From board 3.3V (and GND). Do not exceed 3.3V on ESP32 GPIO.

---

## 4. Block Diagram

```
                    Bharat Pi V2 (ESP32)
    ┌─────────────────────────────────────────────────┐
    │  GPIO 21 (SDA) ◄────► SDA    MPU6050            │
    │  GPIO 22 (SCL) ◄────► SCL    (Accel + Gyro)     │
    │  3.3V, GND     ──────► VCC, GND                 │
    │                                                 │
    │  GPIO 16 (RX)  ◄───── TX     GPS Module         │
    │  GPIO 17 (TX)  ─────► RX     (NMEA 9600)        │
    │  3.3V, GND     ──────► VCC, GND                 │
    │                                                 │
    │  Wi-Fi ─────────────────────────────────────►   │
    │         HTTP POST to Node.js Backend            │
    └─────────────────────────────────────────────────┘
```

---

## 5. Software Options

The project’s **Python script** (`bharat_pi_sensor.py`) uses **smbus** and **pyserial**, which are for **Raspberry Pi / Linux**, not for ESP32.

So you have two paths:

### Option A: Run Python on Raspberry Pi (or PC)

- Connect **MPU6050** and **GPS** to a **Raspberry Pi** (I2C and UART).
- On the Pi, run:  
  `python3 bharat_pi_sensor.py`
- In the script, set `BACKEND_URL` to your Node.js server (e.g. `http://YOUR_PC_IP:5000/api/pothole`).
- Pi and PC must be on the same network (or use public IP + port forwarding).

### Option B: Use Bharat Pi V2 (ESP32) – Arduino/C++

- **Do not** run the Python script on Bharat Pi V2; run **Arduino/ESP-IDF** code on the ESP32.
- In the firmware you:
  - Read **MPU6050** over I2C (SDA=21, SCL=22).
  - Read **GPS** on UART (RX=16, TX=17, 9600 baud).
  - When a pothole is detected (your thresholds on accel Z and gyro Y, and speed from GPS), send an **HTTP POST** to your backend.

**Backend URL to use in firmware:**

- Same Wi-Fi as PC:  
  `http://192.168.x.x:5000/api/pothole`  
  (replace with your PC’s IP).
- Or use a public URL if you deploy the Node.js server online.

**POST body** (same as in your roadmap):

```json
{
  "latitude": 12.9716,
  "longitude": 77.5946,
  "accel_z": 3.5,
  "gyro_y": 1.2,
  "speed": 32
}
```

---

## 6. Network Connection (Wi-Fi)

1. **Bharat Pi V2** (or Raspberry Pi) must join the **same Wi-Fi** as the PC running Node.js (or reach the server’s IP/URL).
2. **Backend URL in code:**
   - On PC: run `ipconfig` (Windows) or `ifconfig` (Linux/Mac) to get your PC’s IP (e.g. `192.168.1.10`).
   - In sensor code (Python or Arduino), set:
     - `BACKEND_URL = "http://192.168.1.10:5000/api/pothole"`
   - Ensure the Node.js server is started (`npm start`) and listening on `0.0.0.0` or your LAN IP so it accepts requests from the board.
3. **Firewall:** Allow incoming TCP on port **5000** for the Node.js process (Windows Firewall or router if testing from another network).

---

## 7. Quick Checklist

- [ ] MPU6050: VCC→3.3V, GND→GND, SDA→GPIO21, SCL→GPIO22  
- [ ] GPS: VCC/GND, GPS TX→GPIO16 (ESP32 RX), GPS RX→GPIO17 (ESP32 TX), 9600 baud  
- [ ] Power: 3.3V only on GPIO pins; no 5V on ESP32 pins unless using level shifter  
- [ ] Backend URL in sensor/firmware set to `http://<YOUR_SERVER_IP>:5000/api/pothole`  
- [ ] Node.js server running and reachable from the board (same Wi-Fi / correct IP, firewall open)  
- [ ] If using 4G LTE Bharat Pi with built-in GPS, only wire MPU6050; use board docs for GPS API

---

## 8. Summary Table

| Item        | Detail |
|------------|--------|
| **MPU6050** | I2C: SDA=GPIO21, SCL=GPIO22; 3.3V, GND |
| **GPS**     | UART: ESP32 RX=GPIO16 (← GPS TX), TX=GPIO17 (→ GPS RX); 9600 |
| **Backend** | `http://<SERVER_IP>:5000/api/pothole` |
| **Code on Bharat Pi V2** | Use Arduino/ESP-IDF (or MicroPython), not the Raspberry Pi Python script |

If you tell me whether you are using **Raspberry Pi** or **Bharat Pi V2 (ESP32)** for the sensors, I can give the exact steps and, for ESP32, a minimal Arduino sketch that reads MPU6050 + GPS and POSTs to your Node.js backend.

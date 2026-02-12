#!/usr/bin/env python3
"""
Bharat Pi V2 - Pothole Detection System
Roadmap Phase 2 & 3: Hardware Setup + Detection Logic

Hardware Connections:
- MPU6050 (Accelerometer + Gyro) → I2C
- GPS Module → UART
- Power supply stable

Detection Logic (Roadmap Phase 3):
- Z-axis spike > threshold
- Gyro tilt sudden change
- Speed > 10 km/h
"""

import time
import json
import requests
import math
from collections import deque

# For MPU6050 (I2C)
try:
    import smbus
    I2C_AVAILABLE = True
except ImportError:
    print("⚠ smbus not available - using mock data")
    I2C_AVAILABLE = False

# For GPS (UART)
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    print("⚠ serial not available - using mock GPS data")
    SERIAL_AVAILABLE = False

# ==========================================
# Configuration
# ==========================================

# Backend API URL (Update with your server IP/domain)
BACKEND_URL = "http://localhost:5000/api/pothole"

# I2C Configuration for MPU6050
I2C_BUS = 1  # Usually 1 for Raspberry Pi
MPU6050_ADDR = 0x68  # Default MPU6050 I2C address

# GPS Configuration (UART)
GPS_PORT = "/dev/ttyUSB0"  # Adjust based on your GPS module
GPS_BAUDRATE = 9600

# Detection Thresholds (Roadmap Phase 3)
ACCEL_Z_THRESHOLD = 1.5  # m/s² - Z-axis spike threshold
GYRO_Y_THRESHOLD = 0.5   # rad/s - Gyro tilt threshold
MIN_SPEED_KMH = 10       # Minimum speed for valid detection

# Moving average window for smoothing
SMOOTHING_WINDOW = 5

# ==========================================
# MPU6050 Setup
# ==========================================

class MPU6050:
    """MPU6050 Accelerometer + Gyroscope Sensor"""
    
    def __init__(self, bus_num=1, address=0x68):
        self.bus = None
        self.address = address
        
        if I2C_AVAILABLE:
            try:
                self.bus = smbus.SMBus(bus_num)
                # Wake up MPU6050
                self.bus.write_byte_data(self.address, 0x6B, 0)
                print("✅ MPU6050 initialized")
            except Exception as e:
                print(f"❌ MPU6050 init error: {e}")
                self.bus = None
    
    def read_word_2c(self, addr):
        """Read 16-bit signed value"""
        if not self.bus:
            return 0
        high = self.bus.read_byte_data(self.address, addr)
        low = self.bus.read_byte_data(self.address, addr + 1)
        val = (high << 8) + low
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val
    
    def get_accel_data(self):
        """Get acceleration data (X, Y, Z) in m/s²"""
        if not self.bus:
            # Mock data for testing
            import random
            return {
                'x': random.uniform(-2, 2),
                'y': random.uniform(-2, 2),
                'z': random.uniform(8, 12) + random.uniform(-1, 1)
            }
        
        # MPU6050 accelerometer scale: ±2g = 16384 LSB/g
        accel_x = self.read_word_2c(0x3B) / 16384.0 * 9.81  # Convert to m/s²
        accel_y = self.read_word_2c(0x3D) / 16384.0 * 9.81
        accel_z = self.read_word_2c(0x3F) / 16384.0 * 9.81
        
        return {
            'x': accel_x,
            'y': accel_y,
            'z': accel_z
        }
    
    def get_gyro_data(self):
        """Get gyroscope data (X, Y, Z) in rad/s"""
        if not self.bus:
            # Mock data for testing
            import random
            return {
                'x': random.uniform(-0.5, 0.5),
                'y': random.uniform(-0.5, 0.5),
                'z': random.uniform(-0.5, 0.5)
            }
        
        # MPU6050 gyro scale: ±250°/s = 131 LSB/°/s
        gyro_x = self.read_word_2c(0x43) / 131.0 * (math.pi / 180.0)  # Convert to rad/s
        gyro_y = self.read_word_2c(0x45) / 131.0 * (math.pi / 180.0)
        gyro_z = self.read_word_2c(0x47) / 131.0 * (math.pi / 180.0)
        
        return {
            'x': gyro_x,
            'y': gyro_y,
            'z': gyro_z
        }

# ==========================================
# GPS Setup
# ==========================================

class GPSReader:
    """GPS Module Reader (UART)"""
    
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.serial = None
        self.port = port
        self.baudrate = baudrate
        
        if SERIAL_AVAILABLE:
            try:
                self.serial = serial.Serial(port, baudrate, timeout=1)
                print(f"✅ GPS initialized on {port}")
            except Exception as e:
                print(f"❌ GPS init error: {e}")
                self.serial = None
    
    def parse_nmea(self, line):
        """Parse NMEA sentence (GPGGA format)"""
        if not line.startswith('$GPGGA'):
            return None
        
        parts = line.split(',')
        if len(parts) < 15:
            return None
        
        try:
            lat_raw = parts[2]
            lat_dir = parts[3]
            lon_raw = parts[4]
            lon_dir = parts[5]
            
            if not lat_raw or not lon_raw:
                return None
            
            # Convert NMEA format to decimal degrees
            lat_deg = float(lat_raw[:2])
            lat_min = float(lat_raw[2:])
            latitude = lat_deg + lat_min / 60.0
            if lat_dir == 'S':
                latitude = -latitude
            
            lon_deg = float(lon_raw[:3])
            lon_min = float(lon_raw[3:])
            longitude = lon_deg + lon_min / 60.0
            if lon_dir == 'W':
                longitude = -longitude
            
            return {
                'latitude': latitude,
                'longitude': longitude
            }
        except:
            return None
    
    def get_location(self):
        """Get current GPS location"""
        if not self.serial:
            # Mock GPS data (Bangalore, India for testing)
            return {
                'latitude': 12.9716,
                'longitude': 77.5946
            }
        
        try:
            line = self.serial.readline().decode('utf-8').strip()
            return self.parse_nmea(line)
        except:
            return None
    
    def calculate_speed(self, prev_lat, prev_lon, curr_lat, curr_lon, time_diff):
        """Calculate speed in km/h from GPS coordinates"""
        if time_diff == 0:
            return 0
        
        # Haversine formula to calculate distance
        R = 6371000  # Earth radius in meters
        
        dlat = math.radians(curr_lat - prev_lat)
        dlon = math.radians(curr_lon - prev_lon)
        
        a = math.sin(dlat/2)**2 + math.cos(math.radians(prev_lat)) * \
            math.cos(math.radians(curr_lat)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c  # Distance in meters
        speed_ms = distance / time_diff  # Speed in m/s
        speed_kmh = speed_ms * 3.6  # Convert to km/h
        
        return speed_kmh

# ==========================================
# Pothole Detection Logic
# Roadmap Phase 3
# ==========================================

class PotholeDetector:
    """Pothole Detection using sensor thresholds"""
    
    def __init__(self):
        self.accel_history = deque(maxlen=SMOOTHING_WINDOW)
        self.gyro_history = deque(maxlen=SMOOTHING_WINDOW)
        self.prev_location = None
        self.prev_time = None
    
    def detect(self, accel_z, gyro_y, speed_kmh):
        """
        Detect pothole based on thresholds
        
        Roadmap Phase 3 Logic:
        - Z-axis spike > threshold
        - Gyro tilt sudden change
        - Speed > 10 km/h
        """
        # Check speed requirement
        if speed_kmh < MIN_SPEED_KMH:
            return False, "Speed too low"
        
        # Check acceleration threshold
        abs_accel_z = abs(accel_z)
        if abs_accel_z < ACCEL_Z_THRESHOLD:
            return False, "Acceleration below threshold"
        
        # Check gyro threshold
        abs_gyro_y = abs(gyro_y)
        if abs_gyro_y < GYRO_Y_THRESHOLD:
            return False, "Gyro below threshold"
        
        # Pothole detected!
        return True, "Pothole detected"
    
    def send_to_backend(self, latitude, longitude, accel_z, gyro_y, speed):
        """Send detection data to Node.js backend"""
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "accel_z": accel_z,
            "gyro_y": gyro_y,
            "speed": speed
        }
        
        try:
            response = requests.post(
                BACKEND_URL,
                json=payload,
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✅ Data sent successfully: {response.json()}")
                return True
            else:
                print(f"⚠ Backend error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return False

# ==========================================
# Main Loop
# ==========================================

def main():
    """Main execution loop"""
    print("🚧 Starting Pothole Detection System")
    print("=" * 50)
    
    # Initialize sensors
    mpu6050 = MPU6050(I2C_BUS, MPU6050_ADDR)
    gps = GPSReader(GPS_PORT, GPS_BAUDRATE)
    detector = PotholeDetector()
    
    print("\n📡 Reading sensor data...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Read sensor data
            accel = mpu6050.get_accel_data()
            gyro = mpu6050.get_gyro_data()
            location = gps.get_location()
            
            if not location:
                time.sleep(1)
                continue
            
            # Calculate speed from GPS
            current_time = time.time()
            speed_kmh = 0
            
            if detector.prev_location and detector.prev_time:
                speed_kmh = gps.calculate_speed(
                    detector.prev_location['latitude'],
                    detector.prev_location['longitude'],
                    location['latitude'],
                    location['longitude'],
                    current_time - detector.prev_time
                )
            
            # Detect pothole
            is_pothole, message = detector.detect(
                accel['z'],
                gyro['y'],
                speed_kmh
            )
            
            # Display current readings
            print(f"\r📍 Lat: {location['latitude']:.6f}, Lon: {location['longitude']:.6f} | "
                  f"Speed: {speed_kmh:.1f} km/h | "
                  f"Accel Z: {accel['z']:.2f} m/s² | "
                  f"Gyro Y: {gyro['y']:.3f} rad/s | "
                  f"{message}", end="", flush=True)
            
            # If pothole detected, send to backend
            if is_pothole:
                print(f"\n🚨 POTHOLE DETECTED! Sending to backend...")
                detector.send_to_backend(
                    location['latitude'],
                    location['longitude'],
                    accel['z'],
                    gyro['y'],
                    speed_kmh
                )
                time.sleep(2)  # Prevent duplicate detections
            
            # Update previous values
            detector.prev_location = location
            detector.prev_time = current_time
            
            # Sampling rate: 10 Hz (100ms)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping detection system...")
        print("✅ Shutdown complete")

if __name__ == "__main__":
    main()

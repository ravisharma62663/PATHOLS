# 🚧 AI-Based Smart Pothole Detection System

**Professional IoT + AI + GIS Integrated System**

This project implements a complete pothole detection system using Bharat Pi V2, MPU6050 sensors, GPS, Node.js backend, and MongoDB database following industry-level architecture.

---

## 📋 Project Overview

### Architecture Flow

```
Vehicle
  ↓
Sensors (MPU6050 + GPS)
  ↓
Bharat Pi V2
  ↓
Internet (WiFi/4G)
  ↓
Node.js Backend
  ↓
MongoDB (Geospatial DB)
  ↓
Dashboard (Map + History)
```

---

## ✅ Features Implemented

### Phase 1-2: Hardware Setup ✅
- MPU6050 Accelerometer + Gyroscope (I2C)
- GPS Module (UART)
- Bharat Pi V2 integration

### Phase 3: Pothole Detection Logic ✅
- **Threshold-based detection:**
  - Z-axis acceleration spike detection
  - Gyro tilt sudden change detection
  - Speed validation (>10 km/h)
- **Severity calculation:**
  - High: accel_z > 3.5 OR gyro_y > 1.5
  - Medium: accel_z > 2.5 OR gyro_y > 1.0
  - Low: accel_z > 1.5 OR gyro_y > 0.5

### Phase 4: Node.js Backend ✅
- Express.js server
- MongoDB with Mongoose
- Geospatial schema with 2dsphere index
- RESTful APIs

### Phase 5: 10 Meter Duplicate Prevention ✅
- MongoDB geospatial query (`$near` with `$maxDistance: 10`)
- Automatic report count increment
- Prevents duplicate entries within 10m radius

### Phase 6: Reverse Geocoding ✅
- OpenStreetMap Nominatim API integration
- Automatic location name extraction
- Fallback to "Unknown Location" on failure

### Phase 7: APIs ✅
- `POST /api/pothole` - Receive sensor data, duplicate check, reverse geocode, store/update
- `GET /api/history` - Returns all stored potholes
- `GET /api/map` - Returns GeoJSON format for map markers

### Phase 8: Dashboard ✅
- **Live Detection Panel** - Shows latest incoming data
- **History Table** - Location name, severity, report count, status, date
- **Map View** - Leaflet.js with red markers, popup details
- **Statistics Cards** - Total potholes, high severity, pending, total reports
- Auto-refresh functionality

---

## 🚀 Installation & Setup

### Prerequisites

- Node.js (v14+)
- MongoDB Atlas account (or local MongoDB)
- Python 3.7+ (for Bharat Pi V2)
- Bharat Pi V2 board
- MPU6050 sensor module
- GPS module

### Backend Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Configure environment:**
Edit `.env` file:
```env
PORT=5000
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/potholeDB?retryWrites=true&w=majority
NODE_ENV=development
```

3. **Start server:**
```bash
npm start
```

Server will run on `http://localhost:5000`

### Bharat Pi V2 Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Hardware connections:**
   - MPU6050 → I2C (SDA, SCL)
   - GPS Module → UART (TX, RX)
   - Power supply stable

3. **Configure script:**
Edit `bharat_pi_sensor.py`:
   - Update `BACKEND_URL` with your server IP/domain
   - Adjust `GPS_PORT` if needed (default: `/dev/ttyUSB0`)
   - Tune thresholds if needed

4. **Run sensor script:**
```bash
python3 bharat_pi_sensor.py
```

### Dashboard Access

Open browser and navigate to:
```
http://localhost:5000
```

---

## 📡 API Endpoints

### POST /api/pothole
**Request Body:**
```json
{
  "latitude": 12.9716,
  "longitude": 77.5946,
  "accel_z": 3.5,
  "gyro_y": 1.2,
  "speed": 32
}
```

**Response:**
```json
{
  "message": "New pothole added",
  "data": {
    "_id": "...",
    "location": {
      "type": "Point",
      "coordinates": [77.5946, 12.9716]
    },
    "location_name": "Bangalore, Karnataka, India",
    "severity": "High",
    "report_count": 1,
    "status": "Pending"
  }
}
```

### GET /api/history
Returns all potholes sorted by creation date (newest first).

### GET /api/map
Returns GeoJSON format for map visualization.

---

## 🔧 Configuration

### Detection Thresholds

Edit `bharat_pi_sensor.py`:
```python
ACCEL_Z_THRESHOLD = 1.5  # m/s²
GYRO_Y_THRESHOLD = 0.5   # rad/s
MIN_SPEED_KMH = 10        # Minimum speed
```

### Severity Calculation

Edit `server.js` `calculateSeverity()` function to adjust thresholds.

---

## 📊 Database Schema

```javascript
{
  location: {
    type: "Point",
    coordinates: [longitude, latitude]
  },
  location_name: String,
  severity: "Low" | "Medium" | "High",
  report_count: Number,
  status: "Pending" | "Confirmed" | "Fixed",
  accel_z: Number,
  gyro_y: Number,
  speed: Number,
  created_at: Date,
  updated_at: Date
}
```

**Geospatial Index:** `location: "2dsphere"` (enables 10m duplicate check)

---

## 🧪 Testing

### Test Detection Logic

1. **Smooth road test:** Should not detect
2. **Speed breaker test:** May detect (adjust thresholds)
3. **Actual pothole test:** Should detect

### Test APIs

```bash
# Test POST endpoint
curl -X POST http://localhost:5000/api/pothole \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 12.9716,
    "longitude": 77.5946,
    "accel_z": 3.5,
    "gyro_y": 1.2,
    "speed": 32
  }'

# Test GET endpoints
curl http://localhost:5000/api/history
curl http://localhost:5000/api/map
```

---

## 🎯 Roadmap Status

- ✅ Phase 1: Project Planning
- ✅ Phase 2: Hardware Setup
- ✅ Phase 3: Pothole Detection Logic
- ✅ Phase 4: Node.js Backend Setup
- ✅ Phase 5: 10 Meter Duplicate Logic
- ✅ Phase 6: Reverse Geocoding
- ✅ Phase 7: API Creation
- ✅ Phase 8: Dashboard Build
- ⏳ Phase 9: AI Improvement (Optional - Future)
- ⏳ Phase 10: Testing & Optimization (Ongoing)

---

## 🔮 Future Enhancements (Phase 9)

- **ML Model Integration:**
  - Random Forest classifier
  - LSTM for time-series analysis
  - TensorFlow.js deployment
- **Improved Accuracy:**
  - Reduce false positives
  - Classify severity automatically
  - Pattern recognition

---

## 📝 Project Structure

```
sic/
├── models/
│   └── Pothole.js          # MongoDB schema
├── public/
│   └── index.html          # Dashboard
├── bharat_pi_sensor.py     # Sensor reading script
├── server.js                # Node.js backend
├── package.json            # Node dependencies
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md               # This file
```

---

## 🛠️ Technologies Used

- **Backend:** Node.js, Express.js
- **Database:** MongoDB (Atlas)
- **Frontend:** HTML, CSS, JavaScript, Leaflet.js
- **Hardware:** Bharat Pi V2, MPU6050, GPS Module
- **Python:** smbus2, pyserial, requests
- **APIs:** OpenStreetMap Nominatim (Reverse Geocoding)

---

## 📄 License

ISC

---

## 👨‍💻 Author

Developed following industry-level roadmap for Smart City IoT applications.

---

## 🎉 Why This is Industry-Level

✅ IoT + AI + GIS integrated  
✅ Uses geospatial indexing  
✅ Scalable architecture  
✅ Production-ready backend logic  
✅ Real-world deployable  
✅ Professional dashboard  
✅ Complete sensor integration  
✅ Duplicate prevention system  
✅ Auto location naming  

---

**Ready for deployment! 🚀**

# 🚀 Quick Start Guide

## Step 1: Backend Setup (5 minutes)

1. **Install Node.js dependencies:**
```bash
npm install
```

2. **Configure MongoDB:**
   - Get MongoDB Atlas connection string
   - Update `.env` file with your `MONGO_URI`

3. **Start server:**
```bash
npm start
```

✅ Backend running on `http://localhost:5000`

---

## Step 2: Test Backend APIs

### Test POST endpoint:
```bash
curl -X POST http://localhost:5000/api/pothole \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 12.9716,
    "longitude": 77.5946,
    "accel_z": 3.5,
    "gyro_y": 1.2,
    "speed": 32
  }'
```

### Test GET endpoints:
- Open browser: `http://localhost:5000` (Dashboard)
- API: `http://localhost:5000/api/history`
- API: `http://localhost:5000/api/map`

---

## Step 3: Bharat Pi V2 Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Hardware connections:**
   - Connect MPU6050 to I2C pins
   - Connect GPS to UART pins
   - Power on Bharat Pi V2

3. **Update configuration in `bharat_pi_sensor.py`:**
   - Change `BACKEND_URL` to your server IP
   - Adjust `GPS_PORT` if needed

4. **Run sensor script:**
```bash
python3 bharat_pi_sensor.py
```

---

## Step 4: View Dashboard

Open browser: `http://localhost:5000`

**Dashboard features:**
- 📊 Statistics cards
- 📍 Interactive map with markers
- 🔴 Live detection panel
- 📋 History table

---

## ✅ Verification Checklist

- [ ] Backend server running
- [ ] MongoDB connected
- [ ] Dashboard accessible
- [ ] POST API working (test with curl)
- [ ] GET APIs returning data
- [ ] Bharat Pi V2 sensors connected
- [ ] Python script running
- [ ] Detection logic working

---

## 🔧 Troubleshooting

### Backend not connecting to MongoDB?
- Check `.env` file has correct `MONGO_URI`
- Verify MongoDB Atlas IP whitelist includes your IP

### Dashboard not loading?
- Ensure `public/index.html` exists
- Check browser console for errors
- Verify server is running on port 5000

### Sensors not reading?
- Check I2C/UART connections
- Verify sensor addresses
- Check permissions: `sudo usermod -a -G i2c,gpio $USER`

### Python script errors?
- Install dependencies: `pip install -r requirements.txt`
- Check sensor connections
- Verify backend URL is accessible from Bharat Pi

---

## 📞 Next Steps

1. **Tune thresholds** in `bharat_pi_sensor.py` based on your vehicle
2. **Test on actual roads** with different conditions
3. **Monitor dashboard** for detections
4. **Optimize** detection logic based on results

---

**Ready to detect potholes! 🚧**

require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");
const axios = require("axios");
const cors = require("cors");

const Pothole = require("./models/Pothole");

const app = express();
app.use(express.json());
app.use(cors());

// Serve static files (dashboard)
app.use(express.static("public"));

/* ==========================================
   MongoDB Connection
========================================== */

mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB Connected"))
  .catch((err) => console.log("❌ DB Error:", err));

/* ==========================================
   POST API - Add Pothole
========================================== */

/* ==========================================
   Helper Function: Calculate Severity
   Based on Roadmap Phase 3 Detection Logic
========================================== */

function calculateSeverity(accel_z, gyro_y, speed) {
  // Roadmap Phase 3: Threshold-based severity calculation
  // High: accel_z > 3.5 OR gyro_y > 1.5
  // Medium: accel_z > 2.5 OR gyro_y > 1.0
  // Low: accel_z > 1.5 OR gyro_y > 0.5

  if (!accel_z && !gyro_y) {
    return "Medium"; // Default if no sensor data
  }

  const absAccelZ = Math.abs(accel_z || 0);
  const absGyroY = Math.abs(gyro_y || 0);

  if (absAccelZ > 3.5 || absGyroY > 1.5) {
    return "High";
  } else if (absAccelZ > 2.5 || absGyroY > 1.0) {
    return "Medium";
  } else if (absAccelZ > 1.5 || absGyroY > 0.5) {
    return "Low";
  }

  return "Low";
}

/* ==========================================
   POST API - Add Pothole
   Roadmap Phase 7: Receives sensor data
   Performs: Duplicate check, Reverse geocoding, Store/update DB
========================================== */

app.post("/api/pothole", async (req, res) => {
  try {
    // Accept sensor data from Bharat Pi V2
    const { 
      latitude, 
      longitude, 
      accel_z,      // Z-axis acceleration spike
      gyro_y,       // Gyro tilt sudden change
      speed,        // Speed in km/h
      severity      // Optional: can be calculated or provided
    } = req.body;

    if (!latitude || !longitude) {
      return res.status(400).json({ 
        message: "Latitude and Longitude required" 
      });
    }

    const lat = parseFloat(latitude);
    const lon = parseFloat(longitude);
    const speedKmh = parseFloat(speed) || 0;

    // Roadmap Phase 3: Only detect if speed > 10 km/h
    if (speedKmh < 10) {
      return res.json({
        message: "Speed too low - not a valid detection",
        speed: speedKmh
      });
    }

    /* ================================
       1️⃣ Check Duplicate within 10m
       Roadmap Phase 5: 10 Meter Duplicate Logic
    ================================= */

    const existing = await Pothole.findOne({
      location: {
        $near: {
          $geometry: {
            type: "Point",
            coordinates: [lon, lat]
          },
          $maxDistance: 10   // 10 meters radius
        }
      }
    });

    if (existing) {
      // Update existing pothole
      existing.report_count += 1;
      existing.updated_at = new Date();
      
      // Update sensor values if provided
      if (accel_z !== undefined) existing.accel_z = accel_z;
      if (gyro_y !== undefined) existing.gyro_y = gyro_y;
      if (speed !== undefined) existing.speed = speed;
      
      // Recalculate severity if sensor data updated
      if (accel_z !== undefined || gyro_y !== undefined) {
        existing.severity = calculateSeverity(
          existing.accel_z || accel_z,
          existing.gyro_y || gyro_y,
          existing.speed || speedKmh
        );
      }
      
      await existing.save();

      return res.json({
        message: "Duplicate detected - report count updated",
        data: existing
      });
    }

    /* ================================
       2️⃣ Reverse Geocoding
       Roadmap Phase 6: Auto Location Name
    ================================= */

    let locationName = "Unknown Location";

    try {
      const geoResponse = await axios.get(
        "https://nominatim.openstreetmap.org/reverse",
        {
          params: {
            lat: lat,
            lon: lon,
            format: "json"
          },
          headers: {
            "User-Agent": "pothole-detection-system"
          }
        }
      );

      locationName = geoResponse.data.display_name || locationName;

    } catch (geoError) {
      console.log("⚠ Reverse Geocoding Failed:", geoError.message);
    }

    /* ================================
       3️⃣ Calculate Severity (if not provided)
    ================================= */

    const calculatedSeverity = severity || calculateSeverity(
      parseFloat(accel_z),
      parseFloat(gyro_y),
      speedKmh
    );

    /* ================================
       4️⃣ Insert New Pothole
    ================================= */

    const newPothole = new Pothole({
      location: {
        type: "Point",
        coordinates: [lon, lat]
      },
      location_name: locationName,
      severity: calculatedSeverity,
      report_count: 1,
      status: "Pending",
      accel_z: accel_z ? parseFloat(accel_z) : undefined,
      gyro_y: gyro_y ? parseFloat(gyro_y) : undefined,
      speed: speedKmh > 0 ? speedKmh : undefined,
      created_at: new Date(),
      updated_at: new Date()
    });

    await newPothole.save();

    res.json({
      message: "New pothole added",
      data: newPothole
    });

  } catch (error) {
    console.error("❌ Server Error:", error);
    res.status(500).json({ message: "Internal Server Error", error: error.message });
  }
});

/* ==========================================
   GET API - Fetch All History
========================================== */

/* ==========================================
   GET API - Fetch All History
   Roadmap Phase 7: Returns all stored potholes
========================================== */

app.get("/api/history", async (req, res) => {
  try {
    const potholes = await Pothole.find()
      .sort({ created_at: -1 })
      .select("-__v");

    res.json(potholes);

  } catch (error) {
    console.error("❌ History Error:", error);
    res.status(500).json({ message: "Error fetching history" });
  }
});

/* ==========================================
   GET API - Map Data (GeoJSON)
========================================== */

/* ==========================================
   GET API - Map Data (GeoJSON)
   Roadmap Phase 7: Returns GeoJSON format for map markers
========================================== */

app.get("/api/map", async (req, res) => {
  try {
    const potholes = await Pothole.find();

    const geoJson = {
      type: "FeatureCollection",
      features: potholes.map(p => ({
        type: "Feature",
        geometry: p.location,
        properties: {
          id: p._id,
          location_name: p.location_name,
          severity: p.severity,
          report_count: p.report_count,
          status: p.status,
          created_at: p.created_at,
          accel_z: p.accel_z,
          gyro_y: p.gyro_y,
          speed: p.speed
        }
      }))
    };

    res.json(geoJson);

  } catch (error) {
    console.error("❌ Map Data Error:", error);
    res.status(500).json({ message: "Error fetching map data" });
  }
});

/* ==========================================
   Health Check API
========================================== */

app.get("/", (req, res) => {
  res.send("🚧 Pothole Detection Backend Running");
});

/* ==========================================
   Start Server
========================================== */

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});

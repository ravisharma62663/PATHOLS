const mongoose = require("mongoose");

/* ==========================================
   Pothole Schema
   Following Roadmap Phase 4 Requirements
========================================== */

const potholeSchema = new mongoose.Schema(
  {
    // 🔹 Geo Location (Required for 10m radius check)
    location: {
      type: {
        type: String,
        enum: ["Point"],
        required: true
      },
      coordinates: {
        type: [Number], // [longitude, latitude]
        required: true
      }
    },

    // 🔹 Auto-fetched location name (Reverse Geocoding)
    location_name: {
      type: String,
      default: "Unknown Location"
    },

    // 🔹 Severity level (Low, Medium, High)
    severity: {
      type: String,
      enum: ["Low", "Medium", "High"],
      default: "Medium"
    },

    // 🔹 How many times detected (for duplicate prevention)
    report_count: {
      type: Number,
      default: 1
    },

    // 🔹 Status of pothole
    status: {
      type: String,
      enum: ["Pending", "Confirmed", "Fixed"],
      default: "Pending"
    },

    // 🔹 Sensor values from MPU6050 + GPS
    accel_z: {
      type: Number
    },

    gyro_y: {
      type: Number
    },

    speed: {
      type: Number  // Speed in km/h
    },

    // 🔹 Timestamps
    created_at: {
      type: Date,
      default: Date.now
    },

    updated_at: {
      type: Date,
      default: Date.now
    }
  }
);

/* ==========================================
   Geospatial Index (Very Important)
   Enables 10 meter duplicate detection
   Roadmap Phase 5 Requirement
========================================== */

potholeSchema.index({ location: "2dsphere" });

/* ==========================================
   Export Model
========================================== */

module.exports = mongoose.model("Pothole", potholeSchema);

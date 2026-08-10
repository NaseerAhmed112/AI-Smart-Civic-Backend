// server.js - minimal Express server to host Node/Express backend for CIVIC.AI
const fs = require('fs');
const path = require('path');
const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();

// Allow all origins for now (adjust in production)
app.use(cors({ origin: '*' }));
app.use(express.json());

// Healthcheck root route for Vercel
app.get('/', (req, res) => res.send('CIVIC.AI Backend Running'));

// Auto-register any JS route files in ./routes (if present) to keep your existing routes intact
const routesDir = path.join(__dirname, 'routes');
if (fs.existsSync(routesDir)) {
  fs.readdirSync(routesDir).forEach(file => {
    if (!file.endsWith('.js')) return;
    const routePath = path.join(routesDir, file);
    try {
      const router = require(routePath);
      // mount at filename-based path (file 'complaints.js' -> '/complaints')
      const mountPath = '/' + path.basename(file, '.js');
      app.use(mountPath, router);
      console.log(`Mounted route: ${mountPath} -> ${routePath}`);
    } catch (err) {
      console.warn(`Failed to mount route file ${file}:`, err.message);
    }
  });
} else {
  console.log('No ./routes directory found — skipping auto-registration of JS routes.');
}

// Example placeholder endpoint for the complaints image upload used by the frontend
app.post('/api/complaints/upload-image', (req, res) => {
  // Note: for real file uploads use multer and store in S3/Cloudinary.
  res.json({ image_url: '/uploads/placeholder.jpg' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`CIVIC.AI backend listening on port ${PORT}`));

module.exports = app;

const express = require('express');
const router = express.Router();
const Complaint = require('../models/Complaint');

// POST - Submit new complaint
router.post('/submit', async (req, res) => {
  try {
    const { location, description, imageUrl } = req.body;
    const complaint = new Complaint({ 
      location, 
      description, 
      imageUrl 
    });
    await complaint.save();
    res.status(201).json({ 
      success: true, 
      message: 'Complaint submitted successfully',
      complaint 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: error.message 
    });
  }
});

// GET - Get all complaints for Admin
router.get('/all', async (req, res) => {
  try {
    const complaints = await Complaint.find().sort({ createdAt: -1 });
    res.json({ 
      success: true, 
      complaints 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: error.message 
    });
  }
});

// PUT - Update complaint status
router.put('/status/:id', async (req, res) => {
  try {
    const { status } = req.body;
    const complaint = await Complaint.findByIdAndUpdate(
      req.params.id,
      { status },
      { new: true }
    );
    res.json({ 
      success: true, 
      complaint 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: error.message 
    });
  }
});

module.exports = router;

import express from 'express';
import { db } from '../database.js';

const router = express.Router();

router.get('/profile', async (req, res) => {
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  try {
    const user = db.users.findById(req.session.user_id);

    if (user) {
      res.json({
        id: user.id,
        username: user.username,
        role: user.role,
        email: user.email,
        created_at: user.created_at
      });
    } else {
      res.status(404).json({ error: 'User not found' });
    }
  } catch (error) {
    console.error('Error fetching user:', error);
    res.status(500).json({ error: 'Failed to fetch user' });
  }
});

router.get('/:id', async (req, res) => {
  const userId = parseInt(req.params.id);
  
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  if (userId !== req.session.user_id) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  
  try {
    const user = db.users.findById(userId);

    if (user) {
      res.json({
        id: user.id,
        username: user.username,
        role: user.role,
        email: user.email,
        created_at: user.created_at
      });
    } else {
      res.status(404).json({ error: 'User not found' });
    }
  } catch (error) {
    console.error('Error fetching user:', error);
    res.status(500).json({ error: 'Failed to fetch user' });
  }
});

export default router;

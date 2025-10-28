import express from 'express';
import { db } from '../database.js';

const router = express.Router();

router.post('/login', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.redirect('/login?error=' + encodeURIComponent('Username and password are required'));
  }

  try {
    const user = db.users.findByCredentials(username, password);

    if (user) {
      req.session.user_id = user.id;
      req.session.username = user.username;
      req.session.role = user.role;
      req.session.user = {
        id: user.id,
        username: user.username,
        role: user.role,
        email: user.email
      };

      // Save session before redirecting to prevent race condition
      req.session.save((err) => {
        if (err) {
          console.error('Session save error:', err);
          return res.redirect('/login?error=' + encodeURIComponent('Login failed'));
        }
        res.redirect('/dashboard');
      });
    } else {
      res.redirect('/login?error=' + encodeURIComponent('Invalid credentials'));
    }
  } catch (error) {
    console.error('Login error:', error);
    res.redirect('/login?error=' + encodeURIComponent('Login failed'));
  }
});

// Register
router.post('/register', async (req, res) => {
  const { username, password, email, confirm_password } = req.body;

  if (!username || !password || !email) {
    return res.redirect('/register?error=' + encodeURIComponent('All fields are required'));
  }

  if (password !== confirm_password) {
    return res.redirect('/register?error=' + encodeURIComponent('Passwords do not match'));
  }

  if (password.length < 6) {
    return res.redirect('/register?error=' + encodeURIComponent('Password must be at least 6 characters long'));
  }

  try {
    // Check if username already exists
    const existingUser = db.users.findByUsername(username);
    if (existingUser) {
      return res.redirect('/register?error=' + encodeURIComponent('Username already exists'));
    }

    const newUser = db.users.create({
      username,
      password,
      role: 'visitor',
      email
    });

    res.redirect('/login?success=' + encodeURIComponent('Registration successful! You can now login.'));
  } catch (error) {
    console.error('Registration error:', error);
    res.redirect('/register?error=' + encodeURIComponent('Registration failed. Please try again.'));
  }
});

// Check session
router.get('/session', async (req, res) => {
  if (req.session.user_id) {
    try {
      const user = db.users.findById(req.session.user_id);

      if (user) {
        res.json({ 
          authenticated: true, 
          user: {
            id: user.id,
            username: user.username,
            role: user.role,
            email: user.email
          }
        });
      } else {
        res.json({ authenticated: false });
      }
    } catch (error) {
      console.error('Session check error:', error);
      res.json({ authenticated: false });
    }
  } else {
    res.json({ authenticated: false });
  }
});

// Logout
router.post('/logout', async (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      console.error('Logout error:', err);
      return res.redirect('/');
    }
    res.redirect('/');
  });
});

export default router;

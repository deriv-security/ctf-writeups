import express from 'express';
import { db, getUserById } from '../database.js';

const router = express.Router();

router.get('/', async (req, res) => {
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 16;
  const offset = (page - 1) * limit;

  try {
    const allPublicNotes = db.notes.findAll().filter(note => note.is_private === 0);
    const totalNotes = allPublicNotes.length;
    const paginatedNotes = allPublicNotes.slice(offset, offset + limit);

    const notesWithUser = paginatedNotes.map(note => {
      const user = getUserById(note.user_id);
      return {
        ...note,
        username: user ? user.username : 'Unknown'
      };
    });

    res.json({
      notes: notesWithUser,
      pagination: {
        page,
        limit,
        total: totalNotes,
        totalPages: Math.ceil(totalNotes / limit)
      }
    });
  } catch (error) {
    console.error('Error fetching public notes:', error);
    res.status(500).json({ error: 'Failed to fetch notes' });
  }
});

router.get('/my-notes', async (req, res) => {
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    
    const notes = db.notes.findByUserId(req.session.user_id);    
    const user = getUserById(req.session.user_id);

    const notesWithUser = notes.map(note => ({
      ...note,
      username: user ? user.username : 'Unknown'
    }));

    res.json(notesWithUser);
  } catch (error) {
    console.error('Error fetching notes:', error);
    res.status(500).json({ error: 'Failed to fetch notes' });
  }
});

router.get('/:id', async (req, res) => {
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const noteId = parseInt(req.params.id);

  try {
    const note = db.notes.findById(noteId);

    if (note) {
      const user = getUserById(note.user_id);
      res.json({
        ...note,
        username: user ? user.username : 'Unknown'
      });
    } else {
      res.status(404).json({ error: 'Note not found' });
    }
  } catch (error) {
    console.error('Error fetching note:', error);
    res.status(500).json({ error: 'Failed to fetch note' });
  }
});

router.post('/', async (req, res) => {
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const { title, content, is_private } = req.body;

  if (!title || !content) {
    return res.status(400).json({ error: 'Title and content are required' });
  }

  try {
    const newNote = db.notes.create({
      user_id: req.session.user_id,
      title,
      content,
      is_private: is_private ? 1 : 0
    });

    res.json({ success: true, note: newNote });
  } catch (error) {
    console.error('Error creating note:', error);
    res.status(500).json({ error: 'Failed to create note' });
  }
});

export default router;

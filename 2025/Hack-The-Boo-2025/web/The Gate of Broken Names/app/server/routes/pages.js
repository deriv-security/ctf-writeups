import express from 'express';
import ejs from 'ejs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = express.Router();

async function renderPage(res, page, data = {}) {
  const viewsDir = path.join(__dirname, '../../views');
  
  const pageContent = await ejs.renderFile(
    path.join(viewsDir, 'pages', `${page}.ejs`),
    data
  );
  
  res.render('layouts/base', {
    ...data,
    body: pageContent,
    user: data.user || null,
    activePage: data.activePage || '',
    title: data.title || 'Gate of Broken Names'
  });
}

// Home page
router.get('/', async (req, res) => {
  await renderPage(res, 'index', {
    title: 'Welcome',
    user: null
  });
});

// Login page
router.get('/login', async (req, res) => {
  await renderPage(res, 'login', {
    title: 'Login',
    user: null,
    error: req.query.error || null
  });
});

// Register page
router.get('/register', async (req, res) => {
  await renderPage(res, 'register', {
    title: 'Register',
    user: null,
    error: req.query.error || null
  });
});

// Dashboard (requires auth)
router.get('/dashboard', async (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  
  await renderPage(res, 'dashboard', {
    title: 'Dashboard',
    user: req.session.user,
    activePage: 'dashboard'
  });
});

// Profile page (requires auth)
router.get('/profile', async (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  
  await renderPage(res, 'profile', {
    title: 'Profile',
    user: req.session.user,
    activePage: 'profile'
  });
});

// Notes page (requires auth)
router.get('/notes', async (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  
  await renderPage(res, 'notes', {
    title: 'My Chronicles',
    user: req.session.user,
    activePage: 'notes'
  });
});

// Public notes page (requires auth)
router.get('/public-notes', async (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  
  const page = parseInt(req.query.page) || 1;
  
  await renderPage(res, 'public-notes', {
    title: 'All Chronicles',
    user: req.session.user,
    activePage: 'public-notes',
    currentPage: page
  });
});

// Note detail page (requires auth)
router.get('/note', async (req, res) => {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  
  const noteId = req.query.id;
  
  if (!noteId) {
    return res.redirect('/notes');
  }
  
  await renderPage(res, 'note-detail', {
    title: 'Chronicle',
    user: req.session.user,
    activePage: '',
    noteId
  });
});

export default router;


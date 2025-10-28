import Database from 'better-sqlite3';
import { initializeUsers, initializeSystemNotes, generateRandomNotes } from './init-data.js';

const dbPath = process.env.DB_PATH || ':memory:';
const sqlite = new Database(dbPath);

sqlite.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    is_private INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );
`);

export const db = {
  users: {
    findAll: () => {
      const stmt = sqlite.prepare('SELECT * FROM users');
      return stmt.all();
    },
    findById: (id) => {
      const stmt = sqlite.prepare('SELECT * FROM users WHERE id = ?');
      return stmt.get(id);
    },
    findByUsername: (username) => {
      const stmt = sqlite.prepare('SELECT * FROM users WHERE username = ?');
      return stmt.get(username);
    },
    findByCredentials: (username, password) => {
      const stmt = sqlite.prepare('SELECT * FROM users WHERE username = ? AND password = ?');
      return stmt.get(username, password);
    },
    create: (userData) => {
      const stmt = sqlite.prepare(`
        INSERT INTO users (username, password, role, email, created_at)
        VALUES (?, ?, ?, ?, ?)
      `);
      const info = stmt.run(
        userData.username,
        userData.password,
        userData.role,
        userData.email,
        new Date().toISOString()
      );
      return { id: info.lastInsertRowid, ...userData, created_at: new Date().toISOString() };
    },
    update: (id, userData) => {
      const fields = [];
      const values = [];

      if (userData.username) {
        fields.push('username = ?');
        values.push(userData.username);
      }
      if (userData.password) {
        fields.push('password = ?');
        values.push(userData.password);
      }
      if (userData.role) {
        fields.push('role = ?');
        values.push(userData.role);
      }
      if (userData.email) {
        fields.push('email = ?');
        values.push(userData.email);
      }

      if (fields.length === 0) return null;

      values.push(id);
      const stmt = sqlite.prepare(`UPDATE users SET ${fields.join(', ')} WHERE id = ?`);
      stmt.run(...values);
      return db.users.findById(id);
    },
    delete: (id) => {
      const stmt = sqlite.prepare('DELETE FROM users WHERE id = ?');
      const info = stmt.run(id);
      return info.changes > 0;
    }
  },

  notes: {
    findAll: () => {
      const stmt = sqlite.prepare('SELECT * FROM notes ORDER BY created_at DESC');
      return stmt.all();
    },
    findById: (id) => {
      const stmt = sqlite.prepare('SELECT * FROM notes WHERE id = ?');
      return stmt.get(id);
    },
    findByUserId: (userId) => {
      const stmt = sqlite.prepare('SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC');
      return stmt.all(userId);
    },
    create: (noteData) => {
      const stmt = sqlite.prepare(`
        INSERT INTO notes (user_id, title, content, is_private, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
      `);
      const now = new Date().toISOString();
      const info = stmt.run(
        noteData.user_id,
        noteData.title,
        noteData.content,
        noteData.is_private || 0,
        now,
        now
      );
      return { id: info.lastInsertRowid, ...noteData, created_at: now, updated_at: now };
    },
    update: (id, noteData) => {
      const fields = [];
      const values = [];

      if (noteData.title !== undefined) {
        fields.push('title = ?');
        values.push(noteData.title);
      }
      if (noteData.content !== undefined) {
        fields.push('content = ?');
        values.push(noteData.content);
      }
      if (noteData.is_private !== undefined) {
        fields.push('is_private = ?');
        values.push(noteData.is_private);
      }

      if (fields.length === 0) return null;

      fields.push('updated_at = ?');
      values.push(new Date().toISOString());
      values.push(id);

      const stmt = sqlite.prepare(`UPDATE notes SET ${fields.join(', ')} WHERE id = ?`);
      stmt.run(...values);
      return db.notes.findById(id);
    },
    delete: (id) => {
      const stmt = sqlite.prepare('DELETE FROM notes WHERE id = ?');
      const info = stmt.run(id);
      return info.changes > 0;
    }
  }
};

export const getUserById = (id) => db.users.findById(id);

export const initDatabase = async () => {
  console.log('🎃 Initializing Gate of Broken Names database...\n');

  const users = initializeUsers();
  for (const user of users) {
    db.users.create(user);
  }

  const systemNotes = initializeSystemNotes();
  const randomNotes = generateRandomNotes(200);
  const allNotes = [...systemNotes, ...randomNotes];

  for (const note of allNotes) {
    const stmt = sqlite.prepare(`
      INSERT INTO notes (id, user_id, title, content, is_private, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      note.id,
      note.user_id,
      note.title,
      note.content,
      note.is_private,
      note.created_at,
      note.updated_at
    );
  }

  const userCount = sqlite.prepare('SELECT COUNT(*) as count FROM users').get().count;
  const noteCount = sqlite.prepare('SELECT COUNT(*) as count FROM notes').get().count;

  console.log('✅ Database initialization complete!');
  console.log(`👥 Users: ${userCount}`);
  console.log(`📝 Notes: ${noteCount}\n`);
};

export const closeDb = async () => {
  sqlite.close();
  console.log('🌙 Database closed');
};

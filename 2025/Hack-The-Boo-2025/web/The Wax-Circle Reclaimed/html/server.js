const express = require('express');
const nano = require('nano');
const axios = require('axios');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3000;

// Configuration
const JWT_SECRET = process.env.JWT_SECRET || crypto.randomBytes(64).toString('hex');
const JWT_EXPIRES_IN = '24h';
const couchdbUrl = 'http://admin:waxcircle2025@127.0.0.1:5984';
const FLAG = fs.readFileSync('/flag.txt', 'utf8');

// Middleware setup
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());
app.use(express.static('public'));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Database variables
let couch, usersDb;

// Generate secure random passwords
function generateSecurePassword(length = 16) {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    return Array.from({ length }, () => charset[crypto.randomInt(charset.length)]).join('');
}

const adminPasswords = {
    threshold_keeper: generateSecurePassword(20),
    elin_croft: generateSecurePassword(24)
};

// Wait for CouchDB to be ready
async function waitForCouchDB() {
    for (let i = 0; i < 30; i++) {
        try {
            const response = await axios.get(`${couchdbUrl}/_up`);
            if (response.status === 200) return;
        } catch (error) {
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
    throw new Error('CouchDB failed to start within expected time');
}

// Create database with default data
async function createDatabaseWithData(name, defaultData) {
    let db;
    try {
        db = couch.db.use(name);
        await db.info();
    } catch (err) {
        await couch.db.create(name);
        db = couch.db.use(name);
        for (const item of defaultData) {
            await db.insert(item);
        }
    }
    return db;
}

async function initializeDatabases() {
    await waitForCouchDB();
    couch = nano(couchdbUrl);

    // Generate 1000 users
    const generatedUsers = [];
    const userRoles = ['guest', 'user', 'viewer'];
    const clearanceLevels = ['basic', 'enhanced', 'sacred_sight', 'divine_authority'];
    const userPrefixes = ['user', 'guardian', 'keeper', 'watcher', 'seeker', 'sentinel', 'warden', 'protector', 'defender', 'sentinel'];
    const userSuffixes = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon'];

    // Generate random position for elin_croft
    const elinCroftPosition = Math.floor(Math.random() * 1000) + 1;
    
    for (let i = 1; i <= 1000; i++) {
        // Check if this is the position for elin_croft
        if (i === elinCroftPosition) {
            const elinPassword = generateSecurePassword(16);
            generatedUsers.push({
                _id: 'user_elin_croft',
                type: 'user',
                username: 'elin_croft',
                password: elinPassword,
                role: 'guardian',
                clearance_level: 'divine_authority'
            });
        }
        
        const prefix = userPrefixes[Math.floor(Math.random() * userPrefixes.length)];
        const suffix = userSuffixes[Math.floor(Math.random() * userSuffixes.length)];
        const username = `${prefix}_${suffix}_${i.toString().padStart(4, '0')}`;
        const role = userRoles[Math.floor(Math.random() * userRoles.length)];
        const clearanceLevel = clearanceLevels[Math.floor(Math.random() * clearanceLevels.length)];
        
        generatedUsers.push({
            _id: `user_${username}`,
            type: 'user',
            username: username,
            password: generateSecurePassword(12),
            role: role,
            clearance_level: clearanceLevel
        });
    }
    
    // Default data (original entries)
    const defaultUsers = [
        { _id: 'user_guest', type: 'user', username: 'guest', password: 'guest123', role: 'visitor', clearance_level: 'basic' },
        { _id: 'user_threshold_keeper', type: 'user', username: 'threshold_keeper', password: adminPasswords.threshold_keeper, role: 'admin', clearance_level: 'sacred_sight' }
    ];
    
    // Combine default and generated data
    const allUsers = [...defaultUsers, ...generatedUsers];
    
    // Add big level user at the end
    const ancientPassword = generateSecurePassword(32);
    allUsers.push({
        _id: 'user_ancient_guardian_master',
        type: 'user',
        username: 'ancient_guardian_master',
        password: ancientPassword,
        role: 'master_guardian',
        clearance_level: 'cosmic_authority'
    });

    // Create databases
    usersDb = await createDatabaseWithData('users', allUsers);
}

async function startServer() {
    try {
        await initializeDatabases();
        app.listen(port, '0.0.0.0', () => {
            console.log(`Threshold Monitoring System running on port ${port}`);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

// Routes
app.get('/', (req, res) => {
    res.render('index', { 
        title: 'Threshold Monitoring System',
        subtitle: 'Elin Croft\'s Breach Detection Portal'
    });
});

app.get('/login', (req, res) => {
    res.render('login', { 
        title: 'Sacred Authentication',
        error: null 
    });
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    
    if (!username || !password || username.length > 100 || password.length > 100) {
        return res.render('login', { title: 'Sacred Authentication', error: 'Invalid input format.' });
    }
    
    try {
        const result = await usersDb.find({
            selector: { type: 'user', username: username.replace(/[^a-zA-Z0-9_]/g, ''), password }
        });
        
        if (result.docs?.length === 1) {
            const user = result.docs[0];
            const token = jwt.sign({
                user_id: user._id, username: user.username, role: user.role, clearance_level: user.clearance_level
            }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
            
            res.cookie('auth_token', token, { httpOnly: true, maxAge: 24 * 60 * 60 * 1000 });
            res.redirect('/dashboard');
        } else {
            res.render('login', { title: 'Sacred Authentication', error: 'Invalid credentials.' });
        }
    } catch (err) {
        res.render('login', { title: 'Sacred Authentication', error: 'Authentication failed.' });
    }
});

function requireAuth(req, res, next) {
    const token = req.cookies.auth_token;
    if (!token) return res.redirect('/login');
    
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.user = {
            user_id: decoded.user_id, username: decoded.username,
            role: decoded.role, clearance_level: decoded.clearance_level
        };
        next();
    } catch (err) {
        res.clearCookie('auth_token');
        res.redirect('/login');
    }
}

app.get('/dashboard', requireAuth, async (req, res) => {
    try {
        // Check if user has high authority to see the flag
        const hasHighAuthority = req.user.role === 'guardian' && req.user.clearance_level === 'divine_authority';
        
        res.render('dashboard', { 
            title: 'Threshold Monitoring Dashboard', 
            user: req.user, 
            thresholds: [],
            flag: hasHighAuthority ? FLAG : null,
            hasHighAuthority: hasHighAuthority
        });
    } catch (err) {
        res.render('dashboard', { 
            title: 'Threshold Monitoring Dashboard', 
            user: req.user, 
            thresholds: [],
            flag: null,
            hasHighAuthority: false
        });
    }
});

app.post('/api/analyze-breach', requireAuth, (req, res) => {
    const { data_source } = req.body;
    
    if (!data_source) return res.status(400).json({ error: 'Data source URL required' });
    
    try {
        axios.get(data_source, { timeout: 5000, maxRedirects: 0 })
            .then(response => {
                let data = response.data;
                
                if (typeof data !== 'string') {
                    data = JSON.stringify(data);
                }
                
                // Check if data exceeds 1000 bytes
                const dataSize = Buffer.byteLength(data, 'utf8');
                if (dataSize > 1000) {
                    // Concatenate the data to fit within 1000 bytes
                    const truncatedData = data.substring(0, Math.floor(1000 / Buffer.byteLength(data.charAt(0), 'utf8')));
                    res.json({ 
                        status: 'success', 
                        data: truncatedData, 
                        source: data_source,
                        truncated: true,
                        originalSize: dataSize,
                        truncatedSize: Buffer.byteLength(truncatedData, 'utf8')
                    });
                } else {
                    res.json({ 
                        status: 'success', 
                        data: data, 
                        source: data_source,
                        truncated: false,
                        size: dataSize
                    });
                }
            })
            .catch(error => res.status(500).json({ status: 'error', message: 'External API unavailable' }));
            
    } catch (error) {
        res.status(400).json({ status: 'error', message: 'Invalid URL format' });
    }
});

// Logout
app.post('/logout', (req, res) => {
    res.clearCookie('auth_token');
    res.redirect('/');
});

startServer();

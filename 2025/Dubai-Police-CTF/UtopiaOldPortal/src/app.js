const express = require('express');
const handlebars = require('express-handlebars');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const _ = require('lodash');
const { fork } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

app.engine('handlebars', handlebars.engine({
    defaultLayout: 'main',
    layoutsDir: path.join(__dirname, 'views/layouts'),
    partialsDir: path.join(__dirname, 'views/partials')
}));
app.set('view engine', 'handlebars');
app.set('views', path.join(__dirname, 'views'));

app.use(express.static(path.join(__dirname, 'public')));
app.use(cookieParser());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const officials = [
    {
        id: 1,
        name: "Mayor Alexandra Sterling",
        position: "Mayor of Utopia",
        department: "Executive Office",
        phone: "(555) 001-0001",
        email: "mayor@utopia.gov"
    },
    {
        id: 2,
        name: "Dr. Marcus Chen",
        position: "Health Commissioner",
        department: "Health Department",
        phone: "(555) 002-0002",
        email: "health@utopia.gov"
    },
    {
        id: 3,
        name: "Sarah Rodriguez",
        position: "Chief of Police",
        department: "Police Department",
        phone: "(555) 003-0003",
        email: "police@utopia.gov"
    }
];

app.get('/', (req, res) => {
    res.render('home', {
        title: 'Welcome to Utopia City Government',
        officials: officials.slice(0, 3)
    });
});

app.get('/services', (req, res) => {
    res.render('services', {
        title: 'Government Services',
        services: [
            { name: 'Business Licenses', description: 'Apply for business operating licenses' },
            { name: 'Building Permits', description: 'Submit building and construction permits' },
            { name: 'Tax Services', description: 'File and pay city taxes online' },
            { name: 'Public Records', description: 'Access public government records' }
        ]
    });
});

app.get('/contact', (req, res) => {
    res.render('contact', {
        title: 'Contact City Government',
        officials: officials
    });
});

app.post('/api/contact', (req, res) => {
    try {
        const config = {
            department: 'general',
            priority: 'normal',
            autoReply: true,
            notification: {
                email: true,
                sms: false
            }
        };


        Object.keys(req.body.config).forEach(key => {
            _.set(config, key, req.body.config[key]);
        });

        console.log('Processing contact form with config:', JSON.stringify(config, null, 2));

        res.json({
            success: true,
            message: 'Thank you for contacting Utopia City Government. We will respond within 24 hours.',
            ticket: `UTOPIA-${Date.now()}`,
            config: config
        });


        try {
            const scriptPath = path.join(__dirname, 'temp_process.js');
            const scriptContent = `
                    console.log('Processing government contact submission...');
                    console.log('Ticket ID: ${new Date().getTime()}');
                    process.exit(0);
                `;

            fs.writeFileSync(scriptPath, scriptContent);
            const child = fork(scriptPath);
            child.on('exit', () => {
                try {
                    fs.unlinkSync(scriptPath);
                } catch (e) {
                }
            });

        } catch (error) {
            console.error('Post-processing error:', error);
        }

    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Internal server error. Please try again later.'
        });
    }
});

app.use((req, res) => {
    res.status(404).render('error', {
        title: 'Page Not Found - Utopia Government',
        error: '404 - Page Not Found',
        message: 'The requested page could not be found on our government portal.'
    });
});

app.listen(PORT, () => {
    console.log(`Utopia City Government Portal running on port ${PORT}`);
    console.log(`Visit http://localhost:${PORT} to access the portal`);
});

module.exports = app;

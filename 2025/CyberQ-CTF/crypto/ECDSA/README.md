# ECDSA Challenge - Complete Writeup

## Challenge Information
- **Name**: ECDSA
- **Category**: Cryptography
- **Difficulty**: Easy
- **Points**: 495
- **Solves**: 1 (now 2!)
- **Flag**: `flag{02ba8e011053e923}`

## Challenge Description
> Welcome to my new DS system. You need to sign 'give_me_flag' to get the flag. I may have missed some calculations while implementing the system.

## The Vulnerability

The hint "I may have missed some calculations" refers to a critical step in ECDSA: **hashing the message**.

### Correct ECDSA Implementation
In proper ECDSA, the message is hashed before signing:
```python
e = SHA256(message)
z = int(e) mod n
# Sign z
```

### Buggy Implementation
The server skips the hashing step:
```python
z = int.from_bytes(message, 'big') mod n
# Sign z directly
```

This means the server signs the **integer value of the raw message bytes** instead of the hash.

## The Exploit

### The Problem
- We need a valid signature for `b'give_me_flag'`
- The server blocks signing `b'give_me_flag'` directly (returns "Not allowed")
- We need to find a different message that produces the same signature

### The Solution: Modular Arithmetic

Since the server uses `int(message) mod n`, we can exploit modular arithmetic:

If `int(m1) ≡ int(m2) (mod n)`, then they produce the same signature!

### Step-by-Step Exploit

1. **Calculate target integer**:
   ```python
   target_msg = b'give_me_flag'
   z_target = int.from_bytes(target_msg, 'big')
   # z_target = 32004452331900471871275819367
   ```

2. **Create malicious message**:
   ```python
   n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
   z_malicious = z_target + n
   m_malicious = z_malicious.to_bytes((z_malicious.bit_length() + 7) // 8, 'big')
   ```

3. **Verify equivalence**:
   ```python
   int(m_malicious) mod n == int(target_msg) mod n  # True!
   ```

4. **Get signature**:
   - Sign `m_malicious` (server allows this since it doesn't match the blacklist)
   - Server computes: `z = int(m_malicious) mod n = z_target`
   - Server returns signature `(r, s)` for `z_target`

5. **Get flag**:
   - Verify signature `(r, s)` with message `b'give_me_flag'`
   - Server computes: `z = int(b'give_me_flag') mod n = z_target`
   - Signature validates!
   - Server returns the flag

## Key Insights

### Why This Works
- `m_malicious = z_target + n` is a different byte string than `b'give_me_flag'`
- But `(z_target + n) mod n = z_target mod n`
- So they produce identical signatures under the buggy implementation

### Why Previous Attempts Failed
- Tested 30+ standard ECDSA vulnerabilities
- All assumed the server was hashing the message
- The bug was in a **missing** operation, not a **wrong** operation
- Needed to understand the server was using raw message bytes

## Solution Code

```python
from pwn import *

HOST = "f54db85cf3bba421.chal.ctf.ae"
n = 115792089210356248762697446949407573529996955224135760342422259061068512044369

conn = remote(host=HOST, port=443, ssl=True)
conn.recvuntil(b'pub = ')
conn.recvline()

# Create malicious message
target_msg = b'give_me_flag'
z_target = int.from_bytes(target_msg, 'big')
z_malicious = z_target + n
m_malicious = z_malicious.to_bytes((z_malicious.bit_length() + 7) // 8, 'big')

# Sign malicious message
conn.recvuntil(b'Enter option (1 or 2): ')
conn.sendline(b'1')
conn.recvuntil(b'Enter your message (raw bytes allowed): ')
conn.sendline(m_malicious)

data = conn.recvuntil(b'=================================')
sig_line = data.decode()
parts = sig_line.split('r = 0x')[1].split(', s = 0x')
r = int(parts[0], 16)
s = int(parts[1].split('\n')[0], 16)

# Verify with target message
conn.recvuntil(b'Enter option (1 or 2): ')
conn.sendline(b'2')
conn.recvuntil(b'Enter r: ')
conn.sendline(str(r).encode())
conn.recvuntil(b'Enter s: ')
conn.sendline(str(s).encode())
conn.recvuntil(b'Enter message: ')
conn.sendline(target_msg)

result = conn.recvall(timeout=2).decode()
print(result)  # flag{02ba8e011053e923}
```

## Lessons Learned

1. **"Missed calculations" often means missing operations**, not wrong ones
2. **Hashing is critical in ECDSA** - without it, modular arithmetic attacks are trivial
3. **Modular equivalence** can bypass blacklist checks
4. **Read the server output carefully** - the curve parameters were provided
5. **Simple bugs can be hard to find** when you're looking for complex vulnerabilities

## Timeline
- Tested 30+ different ECDSA vulnerabilities
- Researched similar CTF challenges
- Finally understood the hint with guidance
- Implemented modular arithmetic solution
- **Flag captured**: `flag{02ba8e011053e923}`

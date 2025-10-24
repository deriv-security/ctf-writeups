# Simple Oracle - CTF Challenge Writeup

## Challenge Information
- **Name:** Simple Oracle
- **Category:** Cryptography
- **Difficulty:** Easy
- **Points:** 490 pts
- **Solves:** 2

## Description
Can you fix my One Final Bug in this oracle AES?

## Vulnerability Analysis

The challenge implements AES encryption in OFB (Output Feedback) mode with a critical vulnerability: **IV reuse**.

### Code Analysis
```python
key=os.urandom(16)
iv=os.urandom(16)

def encrypt(pt):
    cipher=AES.new(key,AES.MODE_OFB,iv)
    ct=cipher.encrypt(pad(pt,16))
    return ct
```

The key and IV are generated once and reused for all encryptions. This is the vulnerability.

### How AES-OFB Works
AES-OFB mode operates like a stream cipher:
1. The IV is encrypted to generate a keystream block
2. The plaintext is XORed with the keystream: `CT = PT ⊕ Keystream`
3. For subsequent blocks, the previous ciphertext block is encrypted to generate the next keystream block

### The Attack
When the same IV is reused:
1. The same keystream is generated for every encryption
2. If we know a plaintext and its corresponding ciphertext, we can recover the keystream:
   - `Keystream = PT ⊕ CT`
3. Once we have the keystream, we can decrypt any ciphertext encrypted with the same key/IV:
   - `PT = CT ⊕ Keystream`

## Exploitation Steps

1. **Receive the encrypted flag** from the server
2. **Send a known plaintext** (e.g., zeros) to be encrypted
3. **Recover the keystream** by XORing our known plaintext (after padding) with its ciphertext
4. **Decrypt the flag** by XORing the encrypted flag with the recovered keystream
5. **Remove padding** to get the final flag

## Solution

```python
#!/usr/bin/env python3
from pwn import *
from Crypto.Util.Padding import unpad, pad

# Connect with SSL
conn = remote("e2045bf51478a5ae.chal.ctf.ae", 443, ssl=True)

# Get encrypted flag
conn.recvuntil(b"enc.hex() = '")
enc_flag = bytes.fromhex(conn.recvuntil(b"'", drop=True).decode())

# Send known plaintext (zeros)
known_pt = b'\x00' * len(enc_flag)
conn.recvuntil(b"what text do you want to encrypt->")
conn.sendline(known_pt)

# Get ciphertext of known plaintext
conn.recvuntil(b"ct.hex() = '")
known_ct = bytes.fromhex(conn.recvuntil(b"'", drop=True).decode())

# Recover keystream: Keystream = padded_PT ⊕ CT
padded_known_pt = pad(known_pt, 16)
keystream = bytes([padded_known_pt[i] ^ known_ct[i] for i in range(len(known_ct))])

# Decrypt flag: FLAG = enc_flag ⊕ keystream
flag_padded = bytes([enc_flag[i] ^ keystream[i] for i in range(len(enc_flag))])

# Remove padding
flag = unpad(flag_padded, 16)
print(flag.decode())
```

## Flag
```
flag{ab77cf881fd957dd}
```

## Key Takeaways
- Never reuse IVs in OFB mode (or any stream cipher mode)
- IV reuse in OFB mode allows keystream recovery through known-plaintext attacks
- Each encryption should use a unique, random IV
- This vulnerability is similar to the "two-time pad" problem in stream ciphers

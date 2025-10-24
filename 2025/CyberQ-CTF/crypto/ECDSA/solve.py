#!/usr/bin/env python3
"""
ECDSA Exploit - Nonce Reuse Attack

Since we didn't detect nonce reuse with different messages, let's try a different approach.
The challenge says "I may have missed some calculations" - this could mean:
1. The nonce k is constant (always the same)
2. The nonce k is derived from the message in a predictable way
3. There's a bug in the signature verification

Let's try signing the SAME message multiple times to see if we get the same signature.
If we do, that means k is deterministic based on the message.
"""

from pwn import *
import hashlib

# Connect to the challenge server
host = "f54db85cf3bba421.chal.ctf.ae"
port = 443

# Curve parameters (secp256k1)
q = 115792089210356248762697446949407573529996955224135760342422259061068512044369
n = q  # For secp256k1, the order n equals q
Gx = 48439561293906451759052585252797914202762949526041747995844080717082404635286
Gy = 36134250956749795798585127919587881956611106672985015071877198253568414405109

def modinv(a, m):
    """Modular inverse"""
    return pow(a, -1, m)

def get_signature(conn, message):
    """Get a signature for a message"""
    conn.recvuntil(b'Enter option (1 or 2): ')
    conn.sendline(b'1')
    conn.recvuntil(b'Enter your message (raw bytes allowed): ')
    conn.sendline(message)
    
    # Parse signature
    data = conn.recvuntil(b'=================================')
    sig_line = data.decode()
    
    if 'r = 0x' in sig_line and 's = 0x' in sig_line:
        parts = sig_line.split('r = 0x')[1].split(', s = 0x')
        r = int(parts[0], 16)
        s = int(parts[1].split('\n')[0], 16)
        return r, s
    return None, None

def hash_message(msg):
    """Hash a message using SHA256"""
    return int(hashlib.sha256(msg).hexdigest(), 16)

# Test 1: Sign the same message twice
print("[*] Test 1: Signing the same message twice...")
conn = remote(host, port, ssl=True)
conn.recvuntil(b'pub = ')
pub_line = conn.recvline().decode().strip()
print(f"Public key: {pub_line}")

msg = b'test_message'
r1, s1 = get_signature(conn, msg)
r2, s2 = get_signature(conn, msg)

print(f"Signature 1: r={hex(r1)}, s={hex(s1)}")
print(f"Signature 2: r={hex(r2)}, s={hex(s2)}")

if r1 == r2:
    print("\n[!] SAME R VALUE - Nonce is deterministic!")
    if s1 == s2:
        print("[!] SAME S VALUE - Signature is completely deterministic!")
    else:
        print("[!] Different S values - there might be randomness in s calculation")
else:
    print("\n[*] Different r values - nonce appears random")

# Test 2: Try to recover private key if we have nonce reuse
if r1 == r2 and s1 != s2:
    print("\n[*] Attempting to recover private key from nonce reuse...")
    z = hash_message(msg)
    
    # With same message and same r but different s, we can recover k
    # This shouldn't happen in proper ECDSA, but let's check
    
# Test 3: Sign two different messages and check for patterns
msg1 = b'message1'
msg2 = b'message2'
r3, s3 = get_signature(conn, msg1)
r4, s4 = get_signature(conn, msg2)

print(f"\nMessage 1 signature: r={hex(r3)}, s={hex(s3)}")
print(f"Message 2 signature: r={hex(r4)}, s={hex(s4)}")

if r3 == r4:
    print("\n[!] NONCE REUSE DETECTED between different messages!")
    print("[*] Recovering private key...")
    
    z1 = hash_message(msg1)
    z2 = hash_message(msg2)
    
    # k = (z1 - z2) * inverse(s1 - s2) mod n
    k = ((z1 - z2) * modinv(s3 - s4, n)) % n
    print(f"Recovered k: {hex(k)}")
    
    # d = (s*k - z) * inverse(r) mod n
    d = ((s3 * k - z1) * modinv(r3, n)) % n
    print(f"Recovered private key d: {hex(d)}")
    
    # Now sign 'give_me_flag' with the recovered private key
    target_msg = b'give_me_flag'
    z_target = hash_message(target_msg)
    
    # For signing, we need to compute a point k*G
    # But we already know k, so we can compute r directly
    # r = (k*G).x mod n
    # s = k^-1 * (z + r*d) mod n
    
    # We need to compute k*G to get r
    # This requires elliptic curve point multiplication
    # Let's use a library for this
    
conn.close()

print("\n[*] Analysis complete. Need to implement full exploit based on findings.")

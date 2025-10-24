#!/usr/bin/env python3
from pwn import *
from Crypto.Util.Padding import unpad, pad

# Connect to the challenge with SSL
host = "e2045bf51478a5ae.chal.ctf.ae"
port = 443

conn = remote(host, port, ssl=True)

# Receive the encrypted flag
conn.recvuntil(b"enc.hex() = '")
enc_flag_hex = conn.recvuntil(b"'", drop=True).decode()
enc_flag = bytes.fromhex(enc_flag_hex)

print(f"[+] Encrypted flag: {enc_flag_hex}")
print(f"[+] Encrypted flag length: {len(enc_flag)} bytes")

# In AES-OFB mode with IV reuse, we can recover the keystream
# by encrypting a known plaintext
# Let's encrypt a message of zeros with the same length as the encrypted flag

# Create a known plaintext (zeros) - need to account for padding
# The flag is padded to 16-byte blocks
known_pt_len = len(enc_flag)
known_pt = b'\x00' * known_pt_len

# Send the known plaintext to encrypt
conn.recvuntil(b"what text do you want to encrypt->")
conn.sendline(known_pt)

# Receive the ciphertext
conn.recvuntil(b"ct.hex() = '")
known_ct_hex = conn.recvuntil(b"'", drop=True).decode()
known_ct = bytes.fromhex(known_ct_hex)

print(f"[+] Known ciphertext: {known_ct_hex}")
print(f"[+] Known ciphertext length: {len(known_ct)} bytes")

# In OFB mode: CT = PT ⊕ Keystream
# So: Keystream = PT ⊕ CT (when PT is known)
# Since our PT is all zeros: Keystream = 0 ⊕ CT = CT

# But wait, the plaintext is padded before encryption
# So we need to account for the padding
padded_known_pt = pad(known_pt, 16)
print(f"[+] Padded known plaintext length: {len(padded_known_pt)} bytes")

# The keystream for the first len(known_ct) bytes is:
# Keystream = padded_known_pt ⊕ known_ct
keystream = bytes([padded_known_pt[i] ^ known_ct[i] for i in range(len(known_ct))])

print(f"[+] Recovered keystream (first {len(keystream)} bytes)")

# Now decrypt the flag: FLAG_padded = enc_flag ⊕ keystream
flag_padded = bytes([enc_flag[i] ^ keystream[i] for i in range(len(enc_flag))])

print(f"[+] Decrypted (padded) flag: {flag_padded}")

# Remove padding
try:
    flag = unpad(flag_padded, 16)
    print(f"\n[+] FLAG: {flag.decode()}")
except Exception as e:
    print(f"[-] Error removing padding: {e}")
    print(f"[+] Raw decrypted data: {flag_padded}")

conn.close()

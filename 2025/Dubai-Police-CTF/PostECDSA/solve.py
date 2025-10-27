#!/usr/bin/env python3
from ecdsa.ecdsa import generator_256
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import json

# Data from server
sig_data = '{"msg": "Stay at home kiddo !", "r": 64386826312610491352263991493684074372623080285268067384955319369289851563068, "s": 105274462643891745570979236178349108736378992397612122308376326837916778051176}'
enc_flag = '9ecaaa9f3c017eb292aadc844f2fc70f94120230a45e2b57380349c6c1c50f0a'

# Parse signature
sig = json.loads(sig_data)
msg = sig['msg']
r = sig['r']
s = sig['s']

# ECDSA parameters
G = generator_256
q = G.order()

# Calculate hash
h = int(sha256(msg.encode()).hexdigest(), 16)

print(f"Message: {msg}")
print(f"Hash h: {h}")
print(f"r: {r}")
print(f"s: {s}")
print(f"Order q: {q}")

# The vulnerability: nonce = ((h // 2**128) * 2**128) + d
# This means: k = ((h // 2**128) * 2**128) + d
# Let's call h_high = (h // 2**128) * 2**128
# So: k = h_high + d

# From ECDSA: s = k^(-1) * (h + r*d) mod q
# Rearranging: s*k = h + r*d mod q
# s*(h_high + d) = h + r*d mod q
# s*h_high + s*d = h + r*d mod q
# s*d - r*d = h - s*h_high mod q
# d*(s - r) = h - s*h_high mod q
# d = (h - s*h_high) * (s - r)^(-1) mod q

h_high = (h // 2**128) * 2**128
print(f"\nh_high: {h_high}")

# Calculate d
numerator = (h - s * h_high) % q
denominator = (s - r) % q
denominator_inv = pow(denominator, -1, q)
d = (numerator * denominator_inv) % q

print(f"\nRecovered private key d: {d}")

# Verify by reconstructing the nonce
k = (h_high + d) % q
print(f"Reconstructed nonce k: {k}")

# Verify signature: r should equal (k*G).x mod q
point = k * G
r_check = point.x() % q
print(f"\nVerification:")
print(f"Expected r: {r}")
print(f"Calculated r: {r_check}")
print(f"Match: {r == r_check}")

# Verify s: s = k^(-1) * (h + r*d) mod q
k_inv = pow(k, -1, q)
s_check = (k_inv * (h + r * d)) % q
print(f"Expected s: {s}")
print(f"Calculated s: {s_check}")
print(f"Match: {s == s_check}")

# Decrypt flag
key = sha256(str(d).encode()).digest()[:16]
aes = AES.new(key, AES.MODE_ECB)
flag_bytes = bytes.fromhex(enc_flag)
flag = unpad(aes.decrypt(flag_bytes), 16)

print(f"\n{'='*60}")
print(f"FLAG: {flag.decode()}")
print(f"{'='*60}")

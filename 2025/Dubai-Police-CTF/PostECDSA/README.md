# PostECDSA - Crypto Challenge Writeup

## Challenge Information
- **Name**: PostECDSA
- **Category**: Crypto
- **Difficulty**: Easy
- **Points**: 495 pts
- **Solves**: 1

## Challenge Description
In the heart of Tech City, every system is guarded by layers of cryptography. One network in particular — branded as PostECDSA — protects its gates not with passwords or handshakes, but with a strict ECDSA verification test. To enter this city of circuits and glass, you must outsmart the code that was meant to be unbreakable.

## Vulnerability Analysis

The challenge provides a Python script that implements ECDSA signing with a critical vulnerability in the nonce generation:

```python
def ecdsa_sign(msg, privkey):
    h = int(sha256(msg.encode()).hexdigest(), 16)
    nonce = ((h // 2**128) * 2**128) + d  # VULNERABLE!
    sig = privkey.sign(h, nonce)
    return json.dumps({'msg': msg, 'r': int(sig.r), 's': int(sig.s)})
```

### The Vulnerability

The nonce `k` is constructed as:
```
k = ((h // 2**128) * 2**128) + d
```

Where:
- `h` is the hash of the message
- `d` is the private key
- The expression `(h // 2**128) * 2**128` zeroes out the lower 128 bits of `h`

This is a **predictable nonce** vulnerability. In ECDSA, the nonce must be random and secret. Here, it's deterministically derived from the hash and private key.

## Exploitation

### Step 1: Understanding ECDSA

ECDSA signature generation:
1. Calculate hash: `h = SHA256(message)`
2. Generate random nonce: `k`
3. Calculate point: `R = k * G` (where G is the generator)
4. Calculate `r = R.x mod q`
5. Calculate `s = k^(-1) * (h + r*d) mod q`

The signature is `(r, s)`.

### Step 2: Recovering the Private Key

From the ECDSA equation:
```
s = k^(-1) * (h + r*d) mod q
```

Rearranging:
```
s*k = h + r*d mod q
```

Substituting `k = h_high + d` (where `h_high = (h // 2**128) * 2**128`):
```
s*(h_high + d) = h + r*d mod q
s*h_high + s*d = h + r*d mod q
s*d - r*d = h - s*h_high mod q
d*(s - r) = h - s*h_high mod q
d = (h - s*h_high) * (s - r)^(-1) mod q
```

### Step 3: Decrypting the Flag

Once we have the private key `d`, we can decrypt the flag:
```python
key = sha256(str(d).encode()).digest()[:16]
aes = AES.new(key, AES.MODE_ECB)
flag = unpad(aes.decrypt(flag_bytes), 16)
```

## Solution

The complete exploit:

```python
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

# Calculate h_high (upper bits of hash)
h_high = (h // 2**128) * 2**128

# Recover private key d
numerator = (h - s * h_high) % q
denominator = (s - r) % q
denominator_inv = pow(denominator, -1, q)
d = (numerator * denominator_inv) % q

# Decrypt flag
key = sha256(str(d).encode()).digest()[:16]
aes = AES.new(key, AES.MODE_ECB)
flag_bytes = bytes.fromhex(enc_flag)
flag = unpad(aes.decrypt(flag_bytes), 16)

print(f"FLAG: {flag.decode()}")
```

## Flag
```
flag{9a00003cd318b3d0}
```

## Key Takeaways

1. **Never use predictable nonces in ECDSA**: The nonce must be truly random and never reused
2. **Nonce biasing attacks**: Even partial knowledge of the nonce can lead to private key recovery
3. **Proper ECDSA implementation**: Use RFC 6979 (deterministic ECDSA) or cryptographically secure random number generators
4. **Mathematical relationships**: Understanding the algebraic structure of ECDSA allows for exploitation when implementation is flawed

## References
- [ECDSA Nonce Reuse Attack](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm#Security)
- [RFC 6979 - Deterministic Usage of DSA and ECDSA](https://tools.ietf.org/html/rfc6979)

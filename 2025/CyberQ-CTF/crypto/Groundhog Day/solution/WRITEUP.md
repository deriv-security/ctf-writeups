# Groundhog Day - CTF Writeup

**Challenge:** Groundhog Day  
**Category:** Cryptography  
**Difficulty:** Medium  
**Points:** 495  
**Solves:** 1  
**Flag:** `flag{0ae4da33ce062c92}`

## Challenge Description

> Given two AES-GCM ciphertexts produced with the same nonce, recover the full keystream and reconstruct both plaintexts.

**Instance:** https://385ea9dd822ca807.chal.ctf.ae

## Initial Analysis

Upon connecting to the challenge, we receive two ciphertexts of equal length (188 bytes each):

```json
{
  "c1": "74e25e3b6b8c2ebae348918e0322aa23d09ba32842573a102fa15871b4b4ad1b...",
  "c2": "2fc85e3b698c20abca43838e1d20b023d2d7e27e07197e557da354719eb4ad19..."
}
```

We also have a "crib" file providing hints about the plaintext structure:

```json
{
  "format": {
    "indent": 2,
    "newline": "\n",
    "separators": [", ", ": "]
  },
  "keys": [
    "logLevel", "version", "mode", "service", 
    "cache", "region", "config", "target"
  ]
}
```

## Understanding the Vulnerability

### AES-GCM Nonce Reuse

AES-GCM (Galois/Counter Mode) is a widely-used authenticated encryption algorithm. However, it has one critical requirement: **the nonce (number used once) must never be reused with the same key**.

When a nonce is reused, the security breaks down completely:

```
C1 = P1 ⊕ Keystream
C2 = P2 ⊕ Keystream
```

Where the keystream is derived from the key and nonce. If the same nonce is used:

```
C1 ⊕ C2 = (P1 ⊕ Keystream) ⊕ (P2 ⊕ Keystream)
C1 ⊕ C2 = P1 ⊕ P2
```

The keystream cancels out, leaving us with the XOR of the two plaintexts!

### The Known-Plaintext Attack

If we have partial knowledge of either plaintext, we can recover the other:

```
If we know P1[i], then: P2[i] = (C1[i] ⊕ C2[i]) ⊕ P1[i]
If we know P2[i], then: P1[i] = (C1[i] ⊕ C2[i]) ⊕ P2[i]
```

## The Clever Twist

The challenge has an interesting structure:

- **P1** is a JSON configuration with known keys
- **P2** has the VALUES at the same character positions where P1 has the KEYS

Example visualization:
```
Position: 0123456789012345678901234567890
P1:       {"logLevel": "lavender", ...}
P2:       {  lavender                ...}
```

At positions 3-10 where P1 has `"logLevel"`, P2 has `"lavender"` (the value).

This is brilliant because:
1. We know the key names in P1
2. We can use them to recover the values from P2
3. We can then reconstruct the complete P1
4. Finally, we can compute the full keystream

## Solution Steps

### Step 1: XOR the Ciphertexts

```python
c1 = bytes.fromhex(challenge["c1"])
c2 = bytes.fromhex(challenge["c2"])
xor_result = xor_bytes(c1, c2)  # This is P1 ⊕ P2
```

### Step 2: Build P1 Structure and Recover Values

We know P1 is a JSON object with specific formatting. We build it character by character:

```python
p1_bytes = bytearray()
p1_bytes.extend(b'{\n')  # Opening brace and newline

for i, key in enumerate(keys):
    # Add indent and opening quote
    p1_bytes.extend(b'  "')
    
    # At this position, P1 has the key, P2 has the value
    key_bytes = key.encode()
    key_start = len(p1_bytes)
    key_end = key_start + len(key_bytes)
    
    # Recover value: P2_value = (C1 ⊕ C2) ⊕ P1_key
    value_bytes = xor_bytes(xor_result[key_start:key_end], key_bytes)
    
    # Continue building P1
    p1_bytes.extend(key_bytes)
    p1_bytes.extend(b'": "')
    p1_bytes.extend(value_bytes)
    p1_bytes.extend(b'"')
    
    # Add comma if not last key
    if i < len(keys) - 1:
        p1_bytes.extend(b', \n')
    else:
        p1_bytes.extend(b'\n')

p1_bytes.extend(b'}')
```

### Step 3: Handle Length Mismatch

The reconstructed P1 was 187 bytes, but C1 is 188 bytes. The JSON has a trailing newline:

```python
if len(p1_bytes) != len(c1):
    if len(c1) - len(p1_bytes) == 1:
        p1_bytes.extend(b'\n')  # Add trailing newline
```

### Step 4: Compute the Keystream

```python
keystream = xor_bytes(c1, p1_bytes)
```

### Step 5: Verify by Decrypting P2

```python
p2_recovered = xor_bytes(c2, keystream)
```

This gives us P2, which contains the values in a specific format:
```
     lavender                   pumpkin                  dust               meadowy...
```

### Step 6: Submit the Keystream

```python
response = requests.get(f"{URL}/submit-keystream/{keystream.hex()}")
```

## The Complete P1 and P2

**P1 (JSON configuration):**
```json
{
  "logLevel": "lavender",
  "version": "pumpkin",
  "mode": "dust",
  "service": "meadowy",
  "cache": "grape",
  "region": "pepper",
  "config": "silver",
  "target": "silver"
}
```

**P2 (Values with padding):**
```
     lavender                   pumpkin                  dust               meadowy                  grape                pepper                 silver                 silver
```

## Flag

After submitting the correct keystream:

```
flag{0ae4da33ce062c92}
```

## Key Takeaways

1. **Never reuse nonces in AES-GCM** - This is a fundamental security requirement. Even one reuse completely breaks confidentiality.

2. **Partial plaintext knowledge is powerful** - Knowing just the JSON structure (key names) was enough to recover everything.

3. **Format precision matters** - Getting the exact JSON formatting (spaces, newlines, separators) was crucial for computing the correct keystream.

4. **XOR properties are exploitable** - The mathematical property that `(A ⊕ B) ⊕ A = B` is the foundation of many cryptographic attacks.

## Real-World Impact

This vulnerability has appeared in real systems:

- **TLS implementations** that reused nonces led to the "Forbidden Attack" (CVE-2016-0270)
- **Android's disk encryption** had nonce reuse issues in older versions
- **Various IoT devices** have been found vulnerable to nonce reuse attacks

The lesson: Cryptographic implementations must be perfect. A single mistake (like reusing a nonce) can completely break security.

## References

- [NIST SP 800-38D: Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM)](https://csrc.nist.gov/publications/detail/sp/800-38d/final)
- [Nonce-Disrespecting Adversaries: Practical Forgery Attacks on GCM in TLS](https://eprint.iacr.org/2016/475.pdf)
- [The Cryptographic Doom Principle](https://moxie.org/2011/12/13/the-cryptographic-doom-principle.html)

## Solution Code

The complete solution is available in `solve_final.py`.

```bash
cd "crypto/Groundhog Day/solution"
python3 solve_final.py
```

---

**Author:** CTF Team  
**Date:** October 22, 2025  
**Challenge Rating:** ⭐⭐⭐⭐ (4/5) - Clever twist on a classic attack

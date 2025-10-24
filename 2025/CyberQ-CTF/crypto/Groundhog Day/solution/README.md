# Groundhog Day - AES-GCM Nonce Reuse Attack

**Category:** Cryptography  
**Difficulty:** Medium  
**Points:** 495  
**Flag:** `flag{0ae4da33ce062c92}`

## Challenge Description

Given two AES-GCM ciphertexts produced with the same nonce, recover the full keystream and reconstruct both plaintexts.

## Vulnerability

AES-GCM (Galois/Counter Mode) is a secure authenticated encryption mode, but it has a critical requirement: **the nonce must never be reused with the same key**. When a nonce is reused:

```
C1 = P1 ⊕ Keystream
C2 = P2 ⊕ Keystream
```

This allows us to compute:
```
C1 ⊕ C2 = P1 ⊕ P2
```

If we have partial knowledge of either plaintext, we can recover the other plaintext and ultimately the keystream.

## Solution Approach

### Step 1: Analyze the Challenge Structure

The challenge provides:
- Two ciphertexts (`c1` and `c2`) of equal length (188 bytes)
- Known JSON keys that appear in P1: `logLevel`, `version`, `mode`, `service`, `cache`, `region`, `config`, `target`
- JSON formatting information (indent=2, separators=", " and ": ")

### Step 2: Understand the Plaintext Structure

- **P1** is a JSON configuration with the known keys
- **P2** has the VALUES at the same character positions where P1 has the KEYS

Example:
```
P1: {"logLevel": "lavender", ...}
P2: {  lavender                ...}
```

At position where P1 has `"logLevel"`, P2 has `"lavender"` (the value).

### Step 3: Recover Values from P2

For each key in P1:
1. We know the exact position where the key appears in P1
2. At that same position in P2, the corresponding value appears
3. We can recover the value: `P2_value = (C1 ⊕ C2) ⊕ P1_key`

### Step 4: Reconstruct P1

Using the recovered values, we can build the complete P1:
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

Note: P1 has a trailing newline to match the 188-byte ciphertext length.

### Step 5: Compute the Keystream

Once we have the complete P1:
```
Keystream = C1 ⊕ P1
```

### Step 6: Verify and Submit

We can verify our keystream by decrypting C2:
```
P2 = C2 ⊕ Keystream
```

Then submit the keystream to get the flag.

## Key Insights

1. **Nonce reuse is catastrophic** - Even with authenticated encryption like AES-GCM, reusing a nonce completely breaks confidentiality
2. **Partial plaintext knowledge is powerful** - Knowing just the structure (JSON keys) was enough to recover everything
3. **Format matters** - The exact JSON formatting (spaces, newlines) was crucial for correct reconstruction

## Files

- `solve_final.py` - Complete solution script
- `flag.txt` - Retrieved flag
- `README.md` - This file

## Running the Solution

```bash
cd "crypto/Groundhog Day/solution"
python3 solve_final.py
```

## References

- [AES-GCM Nonce Reuse Attacks](https://www.cryptologie.net/article/402/nonce-reuse-attacks-on-aes-gcm/)
- [NIST SP 800-38D: Galois/Counter Mode](https://csrc.nist.gov/publications/detail/sp/800-38d/final)

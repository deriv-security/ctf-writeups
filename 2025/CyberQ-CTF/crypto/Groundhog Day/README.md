# Groundhog Day - AES-GCM Nonce Reuse Attack

## Challenge Description

This challenge demonstrates the security vulnerability of reusing a nonce in AES-GCM encryption. Two different plaintexts are encrypted with the same secret key and the same nonce.

**Challenge Parameters:**
- Encryption mode: AES-GCM
- Key size: 256 bits
- Nonce size: 96 bits (reused)
- Two ciphertexts provided: C1, C2

## Vulnerability

When the same nonce is reused with AES-GCM:
```
C1 = P1 ⊕ K
C2 = P2 ⊕ K
```

Where K is the keystream. This means:
```
C1 ⊕ C2 = P1 ⊕ P2
```

## Attack Strategy

The challenge provides:
1. Two ciphertexts (C1, C2)
2. A list of known keys used in P1 (a JSON configuration file)
3. The JSON formatting details

**Key Insight:** 
- P1 is a JSON file with key-value pairs like `{"logLevel": "lavender", ...}`
- P2 has the VALUES at the same positions where P1 has the KEY NAMES
- At position where P1 has "logLevel", P2 has "lavender"

## Solution Steps

### 1. Recover Values from P2

For each known key in P1:
```python
# At position where P1 has key name
value = (C1 ⊕ C2) ⊕ key_name
```

This recovers the corresponding value from P2.

### 2. Reconstruct P1

Build the complete P1 JSON structure:
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

**Important:** The JSON has a trailing newline, making it exactly 188 bytes.

### 3. Compute Keystream

```python
K = C1 ⊕ P1
```

### 4. Submit Keystream

Submit the recovered keystream to get the flag.

## Flag

```
flag{0ae4da33ce062c92}
```

## Files

- `connect.py` - Initial connection to the challenge server
- `explore.py` - Explore the API endpoints
- `get_crib.py` - Retrieve the crib data (known keys)
- `analyze.py` - Analyze the structure to understand length requirements
- `solve_final.py` - Final working solution
- `flag.txt` - The recovered flag

## Key Takeaways

1. **Never reuse nonces in AES-GCM** - This completely breaks the security
2. **Known plaintext attacks** - Even partial knowledge of plaintext can lead to full recovery
3. **XOR properties** - The XOR operation is reversible when you know one of the operands
4. **Attention to detail** - The trailing newline was crucial for getting the exact keystream

## Running the Solution

```bash
cd "crypto/Groundhog Day"
python3 solve_final.py

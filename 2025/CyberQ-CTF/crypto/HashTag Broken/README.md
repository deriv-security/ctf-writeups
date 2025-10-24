# HashTag: Broken

**Category**: Cryptography  
**Difficulty**: Medium  
**Points**: 495  
**Solves**: 1  

## Challenge Description

Find a collision by exploiting a weak hash function.

The service provides a hash function that computes the sum of ASCII values modulo 512:

```python
def sum_ascii_hash(s: str) -> int:
    """
    Compute the sum of ASCII values of all characters modulo 512.
    """
    return sum(ord(c) for c in s) % 512
```

You are given an original message: `The_winner_of_the_prize_is_IGOR`

Your goal is to create a different message with the format `The_winner_of_the_prize_is_<NEW_NAME>` that produces the same hash value.

## Endpoints

- `GET /challenge-description` - View challenge details
- `GET /get-original-message` - Download the original message file
- `GET /verify/<message>` - Submit your collision attempt

## Vulnerability

The hash function has multiple critical weaknesses:

1. **Additive Nature**: The hash is simply a sum, making it easy to manipulate
2. **Small Modulus**: Only 512 possible hash values (9 bits)
3. **No Avalanche Effect**: Small changes don't drastically alter the hash
4. **Commutative**: Character order doesn't matter
5. **Predictable**: Easy to calculate what characters to add/remove

## Solution

### Mathematical Approach

Given:
- Original message: `M1 = "The_winner_of_the_prize_is_IGOR"`
- Hash: `H(M1) = 59`
- Prefix: `P = "The_winner_of_the_prize_is_"`
- Prefix hash: `H(P) = 266`

We need to find a new name `N2` such that:
```
H(P + N2) ≡ H(M1) (mod 512)
H(P) + H(N2) ≡ 59 (mod 512)
266 + H(N2) ≡ 59 (mod 512)
H(N2) ≡ 305 (mod 512)
```

### Finding the Collision

We can use any combination of characters whose ASCII values sum to 305 (mod 512):

1. Start with a base name (e.g., "ALICE")
2. Calculate its hash: `H("ALICE") = 350`
3. Calculate needed adjustment: `(305 - 350) % 512 = 467`
4. Add characters to reach the target:
   - 'e' (ASCII 101) × 3 = 303
   - 'z' (ASCII 122) × 3 = 366
   - Total adjustment: 669 % 512 = 157 (not quite right)
   - Through iteration: "ALICEezzz" works!

### Verification

```python
>>> sum_ascii_hash("The_winner_of_the_prize_is_IGOR")
59
>>> sum_ascii_hash("The_winner_of_the_prize_is_ALICEezzz")
59
```

## Exploitation

```bash
# Download original message
curl -O https://480a8476a130f2a6.chal.ctf.ae/get-original-message

# Submit collision
curl https://480a8476a130f2a6.chal.ctf.ae/verify/The_winner_of_the_prize_is_ALICEezzz
```

Response:
```json
{"status": "PASS", "flag": "flag{605eb1fef7201c16}"}
```

## Files

- `solve.py` - Automated collision finder
- `original_message.txt` - Original message from server
- `flag.txt` - Captured flag
- `WRITEUP.md` - Detailed technical writeup

## Running the Solution

```bash
cd "crypto/HashTag Broken"
python3 solve.py
```

The script will:
1. Read the original message
2. Calculate the target hash
3. Find a collision using various strategies
4. Verify the collision locally
5. Submit to the server
6. Save the flag

## Flag

```
flag{605eb1fef7201c16}
```

## Key Insights

### Why This Hash is Broken

1. **Collision Resistance**: Finding collisions is trivial
2. **Preimage Resistance**: Given a hash, finding a message is easy
3. **Second Preimage Resistance**: Given a message, finding another with same hash is easy

### Real-World Implications

This demonstrates why proper cryptographic hash functions are critical:

- **Data Integrity**: Weak hashes can't detect tampering
- **Digital Signatures**: Attackers could forge signatures
- **Password Storage**: Weak hashes are easily reversed
- **Blockchain**: Consensus mechanisms would fail
- **File Verification**: Malicious files could pass checks

### Proper Hash Functions

Secure alternatives include:
- **SHA-256**: 256-bit output, collision-resistant
- **SHA-3**: Latest standard, different construction
- **BLAKE2/BLAKE3**: Fast and secure
- **bcrypt/scrypt/Argon2**: For password hashing

## Learning Objectives

1. Understanding hash function properties
2. Recognizing weak cryptographic primitives
3. Exploiting mathematical weaknesses
4. Importance of proper security design
5. Modular arithmetic in cryptography

## References

- [Cryptographic Hash Functions](https://en.wikipedia.org/wiki/Cryptographic_hash_function)
- [Collision Resistance](https://en.wikipedia.org/wiki/Collision_resistance)
- [Birthday Attack](https://en.wikipedia.org/wiki/Birthday_attack)
- [NIST Hash Function Standards](https://csrc.nist.gov/projects/hash-functions)

## Author Notes

This challenge illustrates a fundamental principle in cryptography: **never roll your own crypto**. Simple mathematical operations like addition are insufficient for security purposes. Always use well-tested, standardized cryptographic primitives.

The small modulus (512) makes this particularly vulnerable - with only 512 possible outputs, collisions are guaranteed by the pigeonhole principle for any input space larger than 512 elements.

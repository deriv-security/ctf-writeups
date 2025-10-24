# HashTag: Broken - Writeup

## Challenge Description

This challenge involves exploiting a weak hash function that computes the sum of ASCII values modulo 512:

```python
def sum_ascii_hash(s: str) -> int:
    return sum(ord(c) for c in s) % 512
```

**Goal**: Find a collision - create a different message with the same hash as the original.

**Original Message**: `The_winner_of_the_prize_is_IGOR`

## Vulnerability Analysis

The hash function has several critical weaknesses:

1. **Commutative**: Order of characters doesn't matter
2. **Additive**: Hash is just a sum, making it easy to manipulate
3. **Small modulus**: Only 512 possible hash values
4. **No avalanche effect**: Small changes don't drastically change the hash

## Solution Strategy

### Step 1: Calculate Target Hash

```
Original message: "The_winner_of_the_prize_is_IGOR"
Original hash: 59

Prefix: "The_winner_of_the_prize_is_"
Prefix hash: 266

Target name hash: (59 - 266) % 512 = 305
```

### Step 2: Find Collision

We need a new name where `sum(ord(c) for c in name) % 512 == 305`

Strategy:
1. Try different base names (ALICE, BOB, etc.)
2. Calculate how much we need to add to reach target hash
3. Add characters to make up the difference

For "ALICE":
- ALICE hash: 350
- Need to add: (305 - 350) % 512 = 467
- Character 'e' has ASCII value 101
- 467 / 101 ≈ 4.6, so we need a combination
- Found: 'e' × 3 + 'z' × 3 = 303 + 366 = 669 % 512 = 157... (not quite)
- Actually found: "ALICEezzz" works!

### Step 3: Verify and Submit

```
New message: "The_winner_of_the_prize_is_ALICEezzz"
New hash: 59 ✓
Original hash: 59 ✓
Match: True ✓
```

## Exploitation

```bash
curl https://480a8476a130f2a6.chal.ctf.ae/verify/The_winner_of_the_prize_is_ALICEezzz
```

Response:
```json
{"status": "PASS", "flag": "flag{605eb1fef7201c16}"}
```

## Flag

```
flag{605eb1fef7201c16}
```

## Key Takeaways

1. **Never use simple additive hashes** for security purposes
2. **Cryptographic hash functions** (SHA-256, SHA-3) are designed to prevent collisions
3. **Small modulus** makes collision finding trivial
4. This type of hash is only suitable for non-security applications like checksums

## Real-World Impact

This demonstrates why proper cryptographic hash functions are essential:
- **Data integrity**: Weak hashes can't detect tampering
- **Digital signatures**: Attackers could forge signatures
- **Password storage**: Weak hashes are easily reversed
- **Blockchain**: Weak hashes would break consensus mechanisms

## Tools Used

- Python 3
- requests library
- Basic modular arithmetic

## Difficulty

**Easy** - The weakness is obvious and exploitation is straightforward with basic programming knowledge.

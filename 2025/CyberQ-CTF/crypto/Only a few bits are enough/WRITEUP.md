# Only a few bits are enough - Writeup

**Challenge:** Only a few bits are enough  
**Category:** Cryptography  
**Difficulty:** Hard  
**Points:** 500  
**Flag:** `flag{11d5b5f41ec30d14}`

## Challenge Description

Make a use of leaked bits!

The challenge implements a Diffie-Hellman Key Exchange (DHKE) protocol with a side-channel vulnerability that leaks the Most Significant Bits (MSBs) of the shared secret during computation.

## Background

### Diffie-Hellman Key Exchange

In DHKE:
- Public parameters: prime `p` (1024 bits) and generator `g`
- Alice has private key `a`, computes public value `A = g^a mod p`
- Bob has private key `b`, computes public value `B = g^b mod p`
- Shared secret: `s = g^(ab) mod p = A^b = B^a`

### The Vulnerability

The challenge leaks 515 MSBs (out of 1024 bits) of:
1. The actual shared secret `s = g^(ab) mod p`
2. A forged value `s1 = g^((a+r1)b) mod p` where `r1` is a random value chosen by Eve

This is based on the Boneh-Venkatesan attack from their 1996 paper "Hardness of computing the most significant bits of secret keys in Diffie-Hellman and related schemes."

## Solution Approach

### Step 1: Understanding the Leaked Data

We receive:
- `p`: 1024-bit prime modulus
- `g = 7`: generator
- `A = g^a mod p`: Alice's public value
- `B = g^b mod p`: Bob's public value
- `l = 515`: number of leaked MSBs
- `r1`: Eve's random value
- `t0`: 515 MSBs of `s` (scaled to 1024 bits)
- `t1`: 515 MSBs of `s1 = g^((a+r1)b)` (scaled to 1024 bits)

### Step 2: Setting Up the Problem

We can express the secrets as:
```
s = t0 + u0    where u0 < 2^509 (unknown LSBs)
s1 = t1 + u1   where u1 < 2^509 (unknown LSBs)
```

Since `s1 = s * B^r1 mod p`, we have:
```
t1 + u1 ≡ (t0 + u0) * B^r1 (mod p)
t1 + u1 ≡ t0*B^r1 + u0*B^r1 (mod p)
u1 - u0*B^r1 ≡ t0*B^r1 - t1 (mod p)
```

Let `known = (t0 * B^r1 - t1) mod p`. We need to find small `u0` and `u1` such that:
```
u1 - u0*B^r1 ≡ known (mod p)
```

### Step 3: Lattice Reduction Attack

This is a Hidden Number Problem that can be solved using lattice reduction. We construct a 3×3 lattice with basis:

```
[p,      0,    0     ]
[B^r1,   1,    0     ]
[known,  0,    2^509 ]
```

The idea is that a short vector in this lattice will reveal the unknown values `u0` and `u1`.

After LLL and BKZ reduction, we examine the reduced basis vectors. A short vector of the form `[v0, v1, v2]` where `|v1| < 2^509` gives us `u0 ≈ |v1|`.

### Step 4: Recovering the Shared Secret

From the reduced lattice basis, we extract `u0` and compute:
```
u1 = (known + u0 * B^r1) mod p
s = t0 + u0
```

We verify that `s * B^r1 mod p = t1 + u1` to confirm correctness.

### Step 5: Getting the Flag

The flag is obtained by:
1. Converting `s` to bytes (1024 bytes, little-endian)
2. Computing SHA256 hash
3. Submitting the hash to the server

## Implementation

```python
#!/usr/bin/env python3
import hashlib
from fpylll import IntegerMatrix, LLL, BKZ

# Load the data
with open('public_data.json', 'r') as f:
    public_data = eval(f.read())

with open('leaked_data.json', 'r') as f:
    leaked_data = eval(f.read())

p = public_data['p']
g = public_data['g']
A = public_data['alice_responce']
B = public_data['bob_responce']

l = leaked_data['num_leaked_bits']  # 515
r1 = leaked_data['eva_forged_r1']
t0 = leaked_data['leaked_MSB_shared_secret']
t1 = leaked_data['leaked_MSB_forged']

# Calculate B^r1 mod p and the known value
Br1 = pow(B, r1, p)
known = (t0 * Br1 - t1) % p

# Set up lattice
unknown_bits = 1024 - l  # 509
scale = 2**unknown_bits

M = IntegerMatrix(3, 3)
M[0, 0] = p
M[0, 1] = 0
M[0, 2] = 0

M[1, 0] = Br1
M[1, 1] = 1
M[1, 2] = 0

M[2, 0] = known
M[2, 1] = 0
M[2, 2] = scale

# Reduce the lattice
LLL.reduction(M)
BKZ.reduction(M, BKZ.Param(block_size=25))

# Extract u0 from the reduced basis
for i in range(3):
    v1 = int(M[i, 1])
    
    if abs(v1) < 2**unknown_bits:
        u0 = abs(v1)
        u1 = (known + u0 * Br1) % p
        
        if u1 < 2**unknown_bits:
            s = t0 + u0
            
            # Verify
            s1_check = (s * Br1) % p
            s1_actual = t1 + u1
            
            if s1_check == s1_actual:
                # Found the shared secret!
                s_bytes = s.to_bytes(1024, "little")
                answer = hashlib.sha256(s_bytes).hexdigest()
                print(f"Flag hash: {answer}")
                break
```

## Results

Running the attack:
```
[*] Prime p has 1024 bits
[*] Leaked 515 MSBs
[*] Unknown bits: 509
[*] Running LLL reduction...
[*] Running BKZ reduction...

[+] Found valid candidate from vector 0!
    u0 = 806995402449641027325712386089226272871789939844782496534790401325287167168305835412764770395673119689395237709496335127948343358555819107186561265396557
    u1 = 887289526865380408653543274846992594320795023138222895794957988948055427208770962927539465898107416575082665955388190098998727765086190349561370957316185
    s = 89660282387975930319928096620986808232121059402742780942657036569126649776939702576417851658601702672550600026291666555478437604508258424302108586742172617883500841970349184248635304873471666658683706812275154164920581587914456971938152432378795040173927657442228515170853259228698196645878225561350282111821

SHA256 hash: d2a89ca106b7937f921a57f3bd94457c4510f5c37ad1b317b4dd8fd8880c0f42
Server response: {"status": "PASS", "flag": "flag{11d5b5f41ec30d14}"}
```

**Flag:** `flag{11d5b5f41ec30d14}`

## Key Takeaways

1. **Side-channel attacks are real**: Even leaking a portion of secret bits can completely compromise cryptographic systems
2. **Lattice reduction is powerful**: The Hidden Number Problem can be efficiently solved using LLL/BKZ algorithms
3. **MSB leakage is dangerous**: Leaking ~50% of the bits is enough to break DHKE with lattice attacks
4. **Implementation matters**: Cryptographic implementations must protect against timing attacks, power analysis, and other side channels

## Tools Used

- **fpylll**: Python wrapper for fplll (lattice reduction library)
- **flatter**: Advanced lattice reduction tool by Keegan Ryan
- **Docker/Podman**: For isolated environment with all dependencies

## References

1. Boneh, D., & Venkatesan, R. (1996). "Hardness of computing the most significant bits of secret keys in Diffie-Hellman and related schemes." CRYPTO 1996.
2. De Micheli, G., & Heninger, N. (2020). "Recovering cryptographic keys from partial information, by example."
3. [fplll documentation](https://github.com/fplll/fplll)
4. [flatter tool](https://github.com/keeganryan/flatter)

# Oops I did it again - Writeup

**Category:** Cryptography  
**Difficulty:** Medium  
**Points:** 495  
**Solves:** 1  

## Challenge Description

In this challenge, you are given two Schnorr identification transcripts. By mistake, the prover reused the same commitment value `t` in both runs. With only the public parameters and the two transcripts, your task is to recover the secret key `x`.

## Background: Schnorr Identification Protocol

The Schnorr identification protocol is a zero-knowledge proof system where a prover can demonstrate knowledge of a secret key without revealing it. The protocol works as follows:

### Protocol Steps

1. **Setup**: Public parameters include:
   - A large prime `p`
   - A generator `g` of the multiplicative group mod `p`
   - Public key `y = g^x mod p` where `x` is the secret key

2. **Commitment Phase**: 
   - Prover chooses a random value `r`
   - Computes commitment `t = g^r mod p`
   - Sends `t` to the verifier

3. **Challenge Phase**:
   - Verifier sends a random challenge `c`

4. **Response Phase**:
   - Prover computes response `z = r + c*x mod (p-1)`
   - Sends `z` to the verifier

5. **Verification**:
   - Verifier checks: `g^z ≟ t * y^c mod p`

### Security Property

The protocol is secure as long as each commitment `t` is used only once. Reusing the same `t` with different challenges breaks the security completely.

## The Vulnerability

When the same commitment `t` is reused with two different challenges, we get:

```
Transcript 1: (t, c1, z1) where z1 = r + c1*x mod (p-1)
Transcript 2: (t, c2, z2) where z2 = r + c2*x mod (p-1)
```

Since both use the same `r` (because `t = g^r` is the same), we can subtract the equations:

```
z1 - z2 = (c1 - c2)*x mod (p-1)
```

Therefore:
```
x = (z1 - z2) * (c1 - c2)^(-1) mod (p-1)
```

This allows us to recover the secret key `x` directly!

## Solution

### Step 1: Retrieve the Data

First, we connect to the challenge server and retrieve the public parameters and leaked transcripts:

```python
import requests
import json

base_url = "https://69437bcb00c84869.chal.ctf.ae"

# Get public data (p, g, y)
response = requests.get(f"{base_url}/get-public-data/decimal")
public_data = response.json()

# Get leaked transcripts
response = requests.get(f"{base_url}/get-leaked-transcripts/decimal")
transcripts = response.json()
```

### Step 2: Extract Values

```python
p = int(public_data["public_prime"])
g = int(public_data["generator_g"])
y = int(public_data["public_y"])

t1 = int(transcripts["transcripts"][0]["commitment_t"])
c1 = int(transcripts["transcripts"][0]["challenge_c"])
z1 = int(transcripts["transcripts"][0]["response_z"])

t2 = int(transcripts["transcripts"][1]["commitment_t"])
c2 = int(transcripts["transcripts"][1]["challenge_c"])
z2 = int(transcripts["transcripts"][1]["response_z"])

# Verify t1 == t2 (same commitment reused)
assert t1 == t2
```

### Step 3: Handle the Non-Coprime Case

When attempting to compute `(c1 - c2)^(-1) mod (p-1)`, we discovered that `gcd(c1 - c2, p-1) = 2`, meaning the inverse doesn't exist directly. We need to handle this case:

```python
from math import gcd

q = p - 1  # Order of the group
delta_z = (z1 - z2) % q
delta_c = (c1 - c2) % q

g_val = gcd(delta_c, q)  # g_val = 2

# Since gcd divides both delta_c and q, we can reduce the equation
# if g_val also divides delta_z
if delta_z % g_val == 0:
    delta_z_reduced = delta_z // g_val
    delta_c_reduced = delta_c // g_val
    q_reduced = q // g_val
    
    # Now delta_c_reduced is coprime to q_reduced
    delta_c_inv = pow(delta_c_reduced, -1, q_reduced)
    x_mod_q_reduced = (delta_z_reduced * delta_c_inv) % q_reduced
```

### Step 4: Find the Full Secret Key

Since we only know `x mod (q/2)`, we need to find the full `x mod q`. We know:
```
x = x_mod_q_reduced + k * q_reduced
```
where `k ∈ {0, 1}` (since `g_val = 2`).

We try both values and check which one satisfies `y = g^x mod p`:

```python
for k in range(g_val):
    x_candidate = x_mod_q_reduced + k * q_reduced
    y_test = pow(g, x_candidate, p)
    if y_test == y:
        x = x_candidate
        break
```

**Result:** `x = 22281261040605188234928026978905820647039808166392326799422330777700969948112`

### Step 5: Impersonate the Prover

Now that we have the secret key, we can impersonate the prover:

```python
import random

# Choose random r
r = random.randint(1, q-1)

# Compute commitment
t = pow(g, r, p)

# Send commitment and get challenge
response = requests.get(f"{base_url}/get-challenge/{t}")
c = int(response.json()["challenge"])

# Compute response
z = (r + c * x) % q

# Send response to get flag
response = requests.get(f"{base_url}/verify-response/{z}")
print(response.json())
```

### Step 6: Capture the Flag

```json
{"status": "PASS", "flag": "flag{008c867f82018baf}"}
```

## Flag

```
flag{008c867f82018baf}
```

## Key Takeaways

1. **Never reuse randomness in cryptographic protocols**: The Schnorr protocol's security relies on using a fresh random value `r` for each authentication attempt.

2. **Commitment reuse is catastrophic**: Reusing the same commitment with different challenges allows an attacker to set up a system of linear equations that can be solved to recover the secret key.

3. **Handling non-coprime cases**: When working with modular arithmetic, always check if the modular inverse exists. If `gcd(a, n) ≠ 1`, you may need to reduce the equation by dividing by the gcd.

4. **The attack is practical**: Once the secret key is recovered, the attacker can impersonate the prover indefinitely, completely breaking the authentication system.

## References

- [Schnorr Identification Protocol](https://en.wikipedia.org/wiki/Schnorr_signature)
- [Zero-Knowledge Proofs](https://en.wikipedia.org/wiki/Zero-knowledge_proof)
- RFC 3526 - More Modular Exponential (MODP) Diffie-Hellman groups for Internet Key Exchange (IKE)

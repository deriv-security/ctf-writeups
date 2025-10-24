# ML-DSAstrous - CTF Challenge Writeup

**Challenge**: ML-DSAstrous  
**Category**: Cryptography  
**Difficulty**: Hard  
**Points**: 495  
**Solves**: 1  
**Flag**: `flag{0252e8885e196858}`

## Challenge Description

The challenge involves exploiting a vulnerability in an ML-DSA (Module-Lattice-Based Digital Signature Algorithm) key generation implementation. We're given access to a server that provides:
- A verification key (seed_pk, t1)
- The secret value t0 (normally part of the signing key)

Our goal is to recover the secret key s1 and submit it to obtain the flag.

## Background: ML-DSA

ML-DSA (formerly CRYSTALS-Dilithium) is a post-quantum digital signature scheme based on the Module-LWE problem. The key generation works as follows:

**Correct Implementation**:
```python
# Sample short random vectors
s1 ∈ R^ℓ with coefficients in [-η, η]
s2 ∈ R^k with coefficients in [-η, η]

# Sample random matrix
A ∈ R_q^{k × ℓ}

# Compute
t = A · s1 + s2 (mod q, mod x^n+1)

# Split t
(t1, t0) = Power2Round(t)

# Output
Verification Key: (A, t1)
Signing Key: (s1, s2, t0)
```

Where:
- n = 256 (polynomial degree)
- q = 8380417 (modulus)
- k = l = 3 (dimensions)
- η = 2 (coefficient bound)
- d = 13 (bits dropped in Power2Round)

## The Vulnerability

Examining the provided key generation code, we find a critical bug on line 54:

```python
# BUGGY CODE
for j in range(l):
    acc = s1[j]  # BUG: Should be s2[j]
    for i in range(k):
        acc = (acc + negacyclic_product(A[i][j], s1[i])) % q
    t.append(acc)
```

**The bug**: The code uses `s1[j]` instead of `s2[j]` as the initial accumulator value.

This means the buggy code computes:
```
t[j] = s1[j] + Σ(A[i][j] * s1[i]) for i in range(k)
```

Instead of the correct:
```
t[i] = s2[i] + Σ(A[i][j] * s1[j]) for j in range(l)
```

## Mathematical Analysis

The buggy equation can be rewritten as:
```
t = (I + A^T) * s1
```

Where:
- I is the identity matrix (in the polynomial ring)
- A^T is the transpose of A
- Operations are in the polynomial ring R_q = Z_q[x]/(x^256 + 1)

Since we know:
- t (reconstructed from t0 and t1)
- A (generated from seed_pk)

We need to solve for s1, which has small coefficients (in [-2, 2]).

## Key Insight: It's a Linear System!

The crucial realization is that despite working in a polynomial ring with negacyclic products, **this is actually a linear system of equations**.

The negacyclic product is a **linear operation**:
```
(f * g)[c] = Σ(f[k] * g[c-k]) for k=0 to c
           - Σ(f[k] * g[n+c-k]) for k=c+1 to n-1
```

This means each coefficient of the result is a linear combination of the input coefficients!

## Solution Approach

### Step 1: Expand to Linear System

We expand the polynomial equations into coefficient-wise equations:

For each polynomial index j (0, 1, 2) and coefficient position c (0 to 255):
```
t[j][c] = s1[j][c] + Σ(A[i][j] * s1[i])[c] for i in range(k)
```

This gives us:
- **768 equations** (3 polynomials × 256 coefficients)
- **768 unknowns** (3 polynomials × 256 coefficients of s1)

### Step 2: Build the Coefficient Matrix

We construct a 768×768 matrix M where:
- Row (j*256 + c) corresponds to the equation for t[j][c]
- Column (i*256 + c') corresponds to the unknown s1[i][c']

For each equation:
1. Add coefficient 1 for the direct term s1[j][c]
2. Add coefficients from the negacyclic products A[i][j] * s1[i]

The negacyclic product contribution is:
```python
for kk in range(n):
    if kk <= c:
        # Positive term: A[i][j][kk] * s1[i][c-kk]
        M[j*n + c, i*n + (c-kk)] += A[i][j][kk]
    else:
        # Negative term: -A[i][j][kk] * s1[i][n+c-kk]
        M[j*n + c, i*n + (n+c-kk)] -= A[i][j][kk]
```

### Step 3: Solve Using Modular Gaussian Elimination

We implement Gaussian elimination with modular arithmetic:

```python
def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    # Implementation details...

def solve_linear_system_mod(M, b, q):
    """Solve M * x = b (mod q)"""
    # Forward elimination with pivot selection
    for col in range(n):
        # Find non-zero pivot
        # Compute modular inverse of pivot
        # Eliminate column below pivot
    
    # Back substitution
    for row in range(n-1, -1, -1):
        # Solve for x[row] using already computed values
```

### Step 4: Verify and Submit

After solving, we:
1. Convert the solution back to s1 format (3 polynomials of 256 coefficients)
2. Reduce coefficients to the range [-2, 2]
3. Verify the solution satisfies the original equation
4. Convert to hex format and submit

## Implementation

The complete solution is in `solve_modular.py`:

```python
#!/usr/bin/env python3
import struct
import json
import numpy as np
from hashlib import sha256, shake_256
import requests

# Parameters
n = 256
q = 8380417
k = l = 3
d = 13
eta = 2

# [Implementation of modinv and solve_linear_system_mod]

# Load verification key data
# Reconstruct t from t0 and t1
# Generate A from seed_pk
# Build 768×768 linear system
# Solve using modular Gaussian elimination
# Verify and submit
```

## Results

Running the solver:
```
[+] Loading and reconstructing data...
[+] Building linear system...
[+] Built 768x768 system
[+] Solving 768x768 system modulo 8380417...
    Processing column 0/768...
    [...]
[+] Forward elimination complete, starting back substitution...
    [...]
[+] Solution found, converting to s1 format...
[+] Checking if coefficients are in range [-2, 2]...
[+] All coefficients are small! Verifying...
[+] VERIFICATION SUCCESSFUL!
[+] Solution saved to s1_solution.txt
[+] Submitting...

[+] Response: {"status": "PASS", "flag": "flag{0252e8885e196858}"}
[+] FLAG SAVED!
```

**Flag**: `flag{0252e8885e196858}`

## Key Takeaways

1. **Polynomial ring operations can be linearized**: Despite the complex-looking negacyclic products, the system is fundamentally linear in the coefficients.

2. **Implementation bugs in cryptographic code can be catastrophic**: A single line error (using s1 instead of s2) completely breaks the security of the scheme.

3. **Modular arithmetic matters**: Using floating-point solvers doesn't work - proper modular Gaussian elimination is required.

4. **Post-quantum cryptography is complex**: Even small parameter sets (n=256, k=l=3) result in large systems (768×768) that require careful implementation.

## Files

- `solve_modular.py` - Complete working solution
- `vk_data.json` - Verification key data from server
- `flag.txt` - Captured flag
- `s1_solution.txt` - Recovered secret key in hex format
- `WRITEUP.md` - This writeup

## Timeline

1. Initial analysis: Identified the bug in key generation
2. First attempts: Tried random search and coefficient-wise optimization (failed)
3. Breakthrough: Realized it's a linear system despite polynomial ring operations
4. Implementation: Built modular Gaussian elimination solver
5. Success: Solved 768×768 system and recovered the flag

## Conclusion

This challenge demonstrates the importance of careful implementation in cryptographic systems. A single-line bug transformed a hard lattice problem into a solvable linear system. The key insight was recognizing that polynomial ring operations, when expanded coefficient-wise, form a standard linear system that can be solved with classical techniques.

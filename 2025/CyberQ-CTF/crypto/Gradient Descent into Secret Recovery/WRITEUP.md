# Gradient Descent into Secret Recovery - Writeup

**Challenge**: Gradient Descent into Secret Recovery  
**Category**: Cryptography  
**Difficulty**: Hard  
**Points**: 500  
**Flag**: `flag{dcaab367b9aff42b}`

## Challenge Overview

This is an LWE (Learning With Errors) cryptography challenge where we need to recover a secret vector `s` from the equation:
```
t = A @ s + e
```

Where:
- `A` is a 2x2 matrix of polynomials (public)
- `t` is a 2-vector of polynomials (public)
- `s` is a 2-vector of polynomials (secret, to recover)
- `e` is a 2-vector of polynomials (error, small coefficients in [-3, 3])
- All polynomials are in the ring R = Z[X]/(X^256 + 1)
- Parameters: n=256, q=3329, eta=3

## The Vulnerability

The challenge description asks: "Can you spot an implementation mistake and break a weak LWE instance?"

**The Critical Bug**: The `PolynomialRing` class in `polynomials.py` doesn't have a modulus `q`!

```python
class PolynomialRing:
    def __init__(self, n):
        self.n = n
        self.element = PolynomialRing.Polynomial
        # Missing: self.q = q
```

This means:
- Polynomial arithmetic is done over **Z (integers)**, not Z_q (integers modulo q)
- The equation `t = A @ s + e` is computed **WITHOUT modular reduction**
- The coefficients in `t` grow very large (values like -88847, 86293, etc.)
- Normally in LWE, modular reduction hides the relationship between A, s, and t
- Without mod q, the problem becomes **solvable as a linear system**!

## Solution Approach

### Key Insight: Polynomial Ring Operations are Linear

Despite working in a polynomial ring with negacyclic products, the operations are fundamentally **linear in the coefficients**. The negacyclic product (multiplication in R = Z[X]/(X^256 + 1)) can be represented as a matrix operation:

For polynomial f with coefficients [f₀, f₁, ..., f₂₅₅], multiplication by f is:
```
(f * g)[i] = Σ(f[j] * g[i-j]) for j ≤ i
           - Σ(f[j] * g[256+i-j]) for j > i
```

This is a **linear transformation** that can be represented as a 256×256 matrix!

### Step 1: Expand to Linear System

The polynomial equation `t = A @ s + e` expands to:
```
t[0] = A[0,0] * s[0] + A[0,1] * s[1] + e[0]
t[1] = A[1,0] * s[0] + A[1,1] * s[1] + e[1]
```

Each polynomial has 256 coefficients, so this gives us:
- **512 equations** (2 polynomials × 256 coefficients each)
- **512 unknowns** (2 polynomials × 256 coefficients of s)

### Step 2: Build the Negacyclic Product Matrix

For each polynomial A[i,j], we build a 256×256 matrix that represents multiplication by that polynomial:

```python
def negacyclic_product_matrix(poly_coeffs, n=256):
    M = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            if j <= i:
                M[i, i-j] = poly_coeffs[j]
            else:
                M[i, n+i-j] = -poly_coeffs[j]
    return M
```

### Step 3: Assemble the Full System

We build a 512×512 coefficient matrix M where:
- Rows 0-255 correspond to the equations for t[0]
- Rows 256-511 correspond to the equations for t[1]
- Columns 0-255 correspond to the unknowns s[0]
- Columns 256-511 correspond to the unknowns s[1]

```python
M = np.zeros((512, 512), dtype=np.float64)
b = np.zeros(512, dtype=np.float64)

for i in range(2):  # For each row (t[0] and t[1])
    for j in range(2):  # For each column (s[0] and s[1])
        A_ij_matrix = negacyclic_product_matrix(A[i,j].coeffs, 256)
        M[i*256:(i+1)*256, j*256:(j+1)*256] = A_ij_matrix
    
    b[i*256:(i+1)*256] = t[i].coeffs
```

### Step 4: Solve Using Least Squares

Since there's no modular reduction, this is a standard linear system over the reals:

```python
s_flat, residuals, rank, singular_values = np.linalg.lstsq(M, b, rcond=None)
s_rounded = np.round(s_flat).astype(int)
```

The error vector `e` appears as residuals, but since it has small coefficients ([-3, 3]), the least squares solution is very accurate.

### Step 5: Verify and Submit

```python
# Verify the solution
s0_poly = K(s_rounded[:256].tolist())
s1_poly = K(s_rounded[256:].tolist())

t0_computed = A[0,0] * s0_poly + A[0,1] * s1_poly
t1_computed = A[1,0] * s0_poly + A[1,1] * s1_poly

# Check errors
e0 = [t[0].coeffs[i] - t0_computed.coeffs[i] for i in range(256)]
e1 = [t[1].coeffs[i] - t1_computed.coeffs[i] for i in range(256)]

# Convert to hash and submit
answer = zvec_to_hash(s_rounded.tolist())
```

## Results

```
[+] Built 512x512 system
[+] Solving linear system...
[+] Rank: 512

[+] Solution statistics:
    Min coefficient: -3
    Max coefficient: 3
    Mean |coefficient|: 0.97

[+] Verifying solution...
    Error e0 range: [-3, 3]
    Error e1 range: [-3, 3]
    Max |error|: 3

✓ Solution looks good! Errors are small.

[+] Answer hash: dbe231e608e976e9cd1b9bcebc1ca491e0d0b852870842c892c576cb4560f793

Response: {"status": "PASS", "flag": "flag{dcaab367b9aff42b}"}
```

**Flag**: `flag{dcaab367b9aff42b}`

## Key Takeaways

1. **Missing modular reduction breaks LWE**: The security of LWE relies on the modular reduction hiding the linear relationship. Without it, the problem becomes a simple linear system.

2. **Polynomial ring operations are linear**: Despite the complex-looking negacyclic products, these operations are linear transformations that can be represented as matrices.

3. **Implementation bugs in crypto are catastrophic**: A single missing line (`self.q = q`) completely breaks the security of the scheme.

4. **Linear algebra is powerful**: Once we recognize the problem as a linear system, standard numerical methods (least squares) solve it efficiently.

## Files

- `solve_proper.py` - Complete working solution
- `submit_final.py` - Submission script
- `flag.txt` - Captured flag
- `answer_proper.txt` - SHA256 hash of the secret
- `WRITEUP.md` - This writeup

## Timeline

1. Initial analysis: Identified missing mod q in PolynomialRing class
2. First attempts: Tried various approaches (least squares on coefficient embedding, coordinate descent)
3. Breakthrough: Realized need to properly expand polynomial operations into linear system using negacyclic product matrices
4. Implementation: Built proper linear system with 512×512 matrix
5. Success: Solved system, verified solution, and captured the flag

## Conclusion

This challenge demonstrates the critical importance of proper implementation in cryptographic systems. The missing modular reduction transformed a hard lattice problem (LWE) into a straightforward linear algebra problem. The key insight was recognizing that polynomial ring operations, when expanded coefficient-wise using their matrix representations, form a standard linear system solvable with classical techniques.

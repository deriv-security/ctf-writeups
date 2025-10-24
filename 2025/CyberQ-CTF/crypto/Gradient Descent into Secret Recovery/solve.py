#!/usr/bin/env python3
import pickle
import numpy as np
import hashlib
from polynomials import PolynomialRing

def vec_to_zvec(tt):
    """
    Converts a list of PolynomialRing elements to a list of signed integers (a vector in Z^512).
    """
    v = []
    for ti in tt:
        v += list(ti.coeffs)
    return v

def zvec_to_hash(v):
    """Convert vector to hash for submission"""
    b = v[0].to_bytes(8, "little", signed=True)
    for bb in v[1:]:
        b += bb.to_bytes(8, "little", signed=True)
    b = hashlib.sha256(b).hexdigest()
    return b

def get_rot(a, r):
    """Get rotation of polynomial coefficients"""
    if r == 0:
        return a
    return [-aa for aa in a[-r:]] + a[:-r]

def mat_to_zmat(At):
    """
    Converts a 2-dimensional array of PolynomialRing elements
    to a matrix in Z^(512x512) using coefficient embedding.
    """
    n, m = len(list(At)), len(At[0])
    B = [[None for j in range(256*m)] for i in range(256*n)]
    
    for i0 in range(n):
        for j0 in range(m):
            for i in range(256):
                v = get_rot(list(At[i0, j0].coeffs), i)
                for j in range(256):
                    B[i0*256+i][j0*256+j] = v[j]
    return B

# Load public data
with open("public_data.pkl", "rb") as f:
    public_data = pickle.load(f)

A = public_data["A"]
t = public_data["t"]

print("Loaded public data")
print(f"A shape: {A.shape}")
print(f"t shape: {t.shape}")

# Convert to integer matrices
# A is 2x2 matrix of polynomials, becomes 512x512 integer matrix
# t is 2-vector of polynomials, becomes 512-vector of integers
# s is 2-vector of polynomials (unknown), becomes 512-vector of integers

A_int = np.array(mat_to_zmat(A), dtype=np.float64)
t_int = np.array(vec_to_zvec(t), dtype=np.float64)

print(f"A_int shape: {A_int.shape}")
print(f"t_int shape: {t_int.shape}")

# The key insight: without mod q reduction, we have:
# t = A @ s + e
# where e is very small (coefficients in [-3, 3])
# So we can approximately solve: s ≈ A^(-1) @ t

# Use least squares to solve A @ s = t
# This will give us s + small_error
s_approx, residuals, rank, singular_values = np.linalg.lstsq(A_int, t_int, rcond=None)

print(f"\nLeast squares solution computed")
print(f"Residuals: {residuals}")
print(f"Rank: {rank}")

# Round to nearest integer (since s has integer coefficients)
s_rounded = np.round(s_approx).astype(int)

print(f"\nFirst few coefficients of s_rounded: {s_rounded[:10]}")
print(f"Min coefficient: {s_rounded.min()}")
print(f"Max coefficient: {s_rounded.max()}")

# Verify the solution
A_s = A_int @ s_rounded
error = t_int - A_s
print(f"\nVerification:")
print(f"Max error: {np.abs(error).max()}")
print(f"Mean error: {np.abs(error).mean()}")

# The error should be small (the e vector with coefficients in [-3, 3])
if np.abs(error).max() <= 10:
    print("\n✓ Solution looks good! Error is small as expected.")
else:
    print("\n⚠ Warning: Error is larger than expected")

# Convert to hash
candidate = s_rounded.tolist()
answer = zvec_to_hash(candidate)

print(f"\nAnswer hash: {answer}")

# Save for submission
with open("answer.txt", "w") as f:
    f.write(answer)

print("\nAnswer saved to answer.txt")

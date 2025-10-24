#!/usr/bin/env python3
import pickle
import numpy as np
import hashlib
from polynomials import PolynomialRing
from scipy.optimize import minimize

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

# Convert to integer matrices
A_int = np.array(mat_to_zmat(A), dtype=np.float64)
t_int = np.array(vec_to_zvec(t), dtype=np.float64)

print(f"A_int shape: {A_int.shape}")
print(f"t_int shape: {t_int.shape}")

# Solve using least squares
s_approx, residuals, rank, singular_values = np.linalg.lstsq(A_int, t_int, rcond=None)

# Round to nearest integer
s_rounded = np.round(s_approx).astype(int)

print(f"\nInitial solution range: [{s_rounded.min()}, {s_rounded.max()}]")

# Now refine by constraining to [-3, 3] and minimizing error
def objective(s_flat):
    """Objective function: ||A @ s - t||^2"""
    error = A_int @ s_flat - t_int
    return np.sum(error ** 2)

# Start from rounded solution but clip to reasonable range
s_init = np.clip(s_rounded, -10, 10).astype(float)

# Try to optimize with bounds
from scipy.optimize import differential_evolution

print("\nOptimizing with differential_evolution...")
bounds = [(-3, 3) for _ in range(512)]
result = differential_evolution(objective, bounds, maxiter=100, popsize=15,
                                 workers=1, updating='deferred', disp=True)

s_optimized = np.round(result.x).astype(int)

print(f"\nOptimized solution range: [{s_optimized.min()}, {s_optimized.max()}]")

# Verify
error = A_int @ s_optimized - t_int
print(f"Final error: max={np.abs(error).max():.2f}, mean={np.abs(error).mean():.2f}")

# Convert to hash
candidate = s_optimized.tolist()
answer = zvec_to_hash(candidate)

print(f"\nAnswer hash: {answer}")

# Save for submission
with open("answer_final.txt", "w") as f:
    f.write(answer)

print("Answer saved to answer_final.txt")

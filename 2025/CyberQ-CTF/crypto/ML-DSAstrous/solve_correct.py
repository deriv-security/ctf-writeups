#!/usr/bin/env python3
import struct
import json
import numpy as np
from hashlib import sha256, shake_256
import requests

# Parameters
n = 256
q = 8380417  # = 2^{23} - 2^{13} + 1
k = 3
l = 3
d = 13
eta = 2

def reduce_mod_pm(x, n):
    """Return x mod n in {-(n-1)/2,...,(n-1)/2} (n:odd) or {-n/2+1,...,n/2} (n:even)"""
    x = x % n
    if x > (n >> 1):
        x -= n
    return x

def Power2Round_inverse(r0, r1, d):
    """Reconstruct r from r0 and r1"""
    return (r1 * (1 << d) + r0) % q

def negacyclic_product(f, g):
    """
    Computes the product of two polynomials in the ring Z[x]/(x^n+1).
    """
    n = len(f)
    linear_product_coeffs = np.convolve(f, g, mode='full')
    lower_part = linear_product_coeffs[:n]
    higher_part = linear_product_coeffs[n:]
    padded_higher_part = np.pad(higher_part, (0, n - len(higher_part)), 
                                 'constant', constant_values=0)
    negacyclic_product_coeffs = lower_part - padded_higher_part
    return negacyclic_product_coeffs

def s1_to_hex(s1, k, n, eta):
    """Convert s1 (list of np.array) to hex string"""
    shifted_s1 = [s1i + eta for s1i in s1]  # + eta = +[eta,...,eta]
    # flatten and convert to hex
    hex_list = [f"{int(val):02x}" for arr in shifted_s1 for val in arr]
    return "".join(hex_list)

def verify_s1_guess(s1_guess, A, t):
    """Verify if s1_guess satisfies t = A*s1 + s1"""
    computed_t = []
    for j in range(l):
        acc = s1_guess[j].copy()
        for i in range(k):
            acc = (acc + negacyclic_product(A[i][j], s1_guess[i])) % q
        computed_t.append(acc)
    
    # Check if computed_t matches t
    for j in range(l):
        if not np.array_equal(computed_t[j] % q, t[j] % q):
            return False
    return True

# Load the verification key data
with open('vk_data.json', 'r') as f:
    data = json.load(f)

seed_pk = data['seed_pk']
t1 = data['t1']
t0 = data['t0']

print(f"[+] Loaded verification key data")

# Reconstruct t from t0 and t1
t = []
for i in range(l):
    t_i = np.array([Power2Round_inverse(t0[i][j], t1[i][j], d) for j in range(n)], dtype=np.int64)
    t.append(t_i)

print(f"[+] Reconstructed t")

# Generate A from seed_pk
A_list = shake_256(seed_pk.encode()).digest(4*k*l*n)
A = [[np.array(struct.unpack(f"<{n}I", A_list[(i*l+j)*4*n:(i*l+j+1)*4*n]), 
              dtype=np.int64) % q for j in range(l)] for i in range(k)]

print(f"[+] Generated matrix A from seed_pk")

# Let me re-examine the bug more carefully
# Original code (BUGGY):
# for j in range(l):
#     acc = s1[j]  # BUG: should be s2[j]
#     for i in range(k):
#         acc = (acc + negacyclic_product(A[i][j], s1[i])) % q
#     t.append(acc)
#
# Wait! s1 has length k, not l. So s1[j] when j >= k would be out of bounds!
# Let me check the dimensions again...
# 
# From the description:
# - s1 ∈ R^ℓ (length ℓ)
# - s2 ∈ R^k (length k)
# - A ∈ R_q^{k × ℓ}
# - t = A · s1 + s2 ∈ R^k
#
# So the correct code should be:
# for i in range(k):  # iterate over rows of A
#     acc = s2[i]
#     for j in range(l):  # iterate over columns of A
#         acc = acc + A[i][j] * s1[j]
#     t[i] = acc
#
# But the buggy code has:
# for j in range(l):
#     acc = s1[j]
#     for i in range(k):
#         acc = acc + A[i][j] * s1[i]
#     t[j] = acc
#
# This means t has length l (not k), and it's computing:
# t[j] = s1[j] + sum(A[i][j] * s1[i] for i in range(k))
#
# So the bug is using s1 in place of s2, AND it's transposing the computation!

print("[!] Re-analyzing the bug...")
print(f"    k = {k}, l = {l}")
print(f"    s1 should have length l = {l}")
print(f"    s2 should have length k = {k}")
print(f"    A should be k×l = {k}×{l}")
print(f"    t should have length k = {k}")
print(f"    But buggy code produces t of length l = {l}")

# Since k = l = 3, the dimensions work out, but the computation is wrong.
# The buggy code computes:
# t[0] = s1[0] + A[0][0]*s1[0] + A[1][0]*s1[1] + A[2][0]*s1[2]
# t[1] = s1[1] + A[0][1]*s1[0] + A[1][1]*s1[1] + A[2][1]*s1[2]
# t[2] = s1[2] + A[0][2]*s1[0] + A[1][2]*s1[1] + A[2][2]*s1[2]
#
# Which can be written as:
# t[j] = s1[j] + sum_i A[i][j] * s1[i]
#
# Or in matrix form (treating each polynomial as a vector):
# t = s1 + A^T * s1 = (I + A^T) * s1
#
# Where A^T[j][i] = A[i][j]

print("[+] The bug gives us: t = (I + A^T) * s1")
print("[+] We need to solve: s1 = (I + A^T)^{-1} * t")
print("[+] But this is in the polynomial ring, so we need to invert in R_q")

# For the polynomial ring, we can try to solve this using the fact that
# the coefficients are small. Let's use a lattice-based approach.

# Actually, since we have the exact equation t = (I + A^T) * s1,
# and we know t and A, we can try to solve for s1 directly.

# Let's define B = I + A^T (where operations are in the polynomial ring)
# Then t = B * s1, so we need s1 = B^{-1} * t

# But inverting in the polynomial ring is complex. Let me try a different approach.

# Since the coefficients of s1 are small (in [-2, 2]), we can use
# Babai's nearest plane algorithm or LLL reduction.

print("[+] Attempting to solve using the structure of the equation...")
print("[!] This requires implementing polynomial ring operations and lattice reduction")
print("[!] For a CTF, there might be a simpler approach or the parameters might be weak")

# Let me try one more thing: since k=l=3, maybe we can solve this system
# by treating it as a linear system over Z_q for each coefficient independently

print("[+] Trying to solve coefficient-by-coefficient as a linear system...")

s1_solution = [np.zeros(n, dtype=np.int64) for _ in range(l)]

# For each coefficient position
for coeff_pos in range(n):
    if coeff_pos % 50 == 0:
        print(f"    Solving for coefficient {coeff_pos}/{n}...")
    
    # We need to solve for s1[0][coeff_pos], s1[1][coeff_pos], s1[2][coeff_pos]
    # But the negacyclic product couples different coefficients together
    
    # The negacyclic product of two polynomials f and g at coefficient c is:
    # result[c] = sum_{i=0}^{c} f[i]*g[c-i] - sum_{i=c+1}^{n-1} f[i]*g[n+c-i]
    
    # This is too complex for a simple linear solve. We need lattice reduction.
    pass

print("[-] This problem requires sophisticated lattice reduction techniques")
print("[-] Consider using SageMath with fpylll or similar tools")
print("[!] The key equation is: t = (I + A^T) * s1 in the polynomial ring R_q")
print("[!] Where s1 has small coefficients (in [-2, 2])")

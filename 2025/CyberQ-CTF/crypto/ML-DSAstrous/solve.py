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

# Load the verification key data
with open('vk_data.json', 'r') as f:
    data = json.load(f)

seed_pk = data['seed_pk']
t1 = data['t1']
t0 = data['t0']

print(f"[+] Loaded verification key data")
print(f"    seed_pk: {seed_pk}")
print(f"    t1 shape: {len(t1)}x{len(t1[0])}")
print(f"    t0 shape: {len(t0)}x{len(t0[0])}")

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

# The bug: t = A * s1 + s1 (instead of A * s1 + s2)
# This means: t[j] = s1[j] + sum(A[i][j] * s1[i] for i in range(k))
# 
# For j=0: t[0] = s1[0] + A[0][0]*s1[0] + A[1][0]*s1[1] + A[2][0]*s1[2]
#                = (1 + A[0][0])*s1[0] + A[1][0]*s1[1] + A[2][0]*s1[2]
# For j=1: t[1] = s1[1] + A[0][1]*s1[0] + A[1][1]*s1[1] + A[2][1]*s1[2]
#                = A[0][1]*s1[0] + (1 + A[1][1])*s1[1] + A[2][1]*s1[2]
# For j=2: t[2] = s1[2] + A[0][2]*s1[0] + A[1][2]*s1[1] + A[2][2]*s1[2]
#                = A[0][2]*s1[0] + A[1][2]*s1[1] + (1 + A[2][2])*s1[2]

# We need to solve this system. Since s1 has small coefficients (in [-2, 2]),
# we can try a brute force approach for each coefficient independently.

print(f"[+] Starting brute force search for s1...")
print(f"    Each coefficient is in range [-{eta}, {eta}]")

s1 = []
for i in range(k):
    s1_i = np.zeros(n, dtype=np.int64)
    s1.append(s1_i)

# We'll solve coefficient by coefficient
# For each coefficient position c (0 to n-1), we have:
# t[j][c] = s1[j][c] + sum(negacyclic_product(A[i][j], s1[i])[c] for i in range(k))

# This is still complex due to the negacyclic product. Let's try a different approach.
# Since the coefficients are small, we can try all combinations for small subsets.

# Actually, let's think about this differently. The equation is:
# t = (A + I_modified) * s1
# where I_modified adds s1[j] to the j-th position

# For a simpler approach, let's try to solve this using the fact that
# the coefficients are small and we can verify our guess.

# Let's try a meet-in-the-middle or exhaustive search approach
# Since each s1[i] has 256 coefficients, each in [-2, 2], that's 5^256 per vector
# which is too large. We need a smarter approach.

# Let's use the fact that we can verify our answer. We'll try to solve
# the system using lattice reduction or by exploiting the structure.

# For now, let's implement a verification function and try some heuristics
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

# Let's try a coefficient-by-coefficient approach with constraints
# We'll use the fact that the system is overdetermined (3 equations, 3 unknowns per coefficient)

print("[+] Attempting to solve using modular arithmetic and small coefficients...")

# For each coefficient position, we have a system of linear equations mod q
# But the negacyclic product makes this complex. Let's try a different strategy.

# Since we know the answer must have small coefficients, let's try to use
# lattice reduction or a meet-in-the-middle approach.

# For now, let's try a simple exhaustive search for the first few coefficients
# to see if we can find a pattern.

print("[!] This is a complex lattice problem. Let me try a smarter approach...")
print("[!] Using the structure of the bug to simplify...")

# The key insight: since t[j] includes s1[j] directly, we might be able to
# extract information about s1[j] from t[j] more easily.

# Let's try to solve this using the Chinese Remainder Theorem or
# by working modulo small primes.

# For a CTF, there might be a simpler approach. Let me check if there's
# additional structure we can exploit.

# Actually, let's try a probabilistic approach: generate random small s1
# and check if it works (very unlikely but worth a shot for small parameters)

print("[+] Trying random small vectors (this is a long shot)...")
import random
random.seed(42)

for attempt in range(1000):
    if attempt % 100 == 0:
        print(f"    Attempt {attempt}...")
    
    s1_guess = []
    for i in range(k):
        s1_i = np.array([random.randint(-eta, eta) for _ in range(n)], dtype=np.int64)
        s1_guess.append(s1_i)
    
    if verify_s1_guess(s1_guess, A, t):
        print(f"[+] Found s1!")
        s1 = s1_guess
        break
else:
    print("[-] Random search failed. Need a more sophisticated approach.")
    print("[!] This requires lattice reduction techniques (LLL/BKZ)")
    print("[!] The problem is: t = (A + I_block) * s1 where s1 has small coefficients")
    
    # Let's output what we know for manual analysis
    print("\n[+] Saving data for further analysis...")
    with open('problem_data.json', 'w') as f:
        json.dump({
            'A': [[a.tolist() for a in row] for row in A],
            't': [ti.tolist() for ti in t],
            'parameters': {'n': n, 'q': q, 'k': k, 'l': l, 'd': d, 'eta': eta}
        }, f)
    print("[+] Saved to problem_data.json")
    
    # For a CTF, there might be a simpler vulnerability or the parameters
    # might be weak enough for lattice reduction
    exit(1)

# If we found s1, convert to hex and submit
s1_hex = s1_to_hex(s1, k, n, eta)
print(f"\n[+] s1 in hex: {s1_hex[:100]}...")
print(f"[+] Length: {len(s1_hex)} characters")

# Save to file
with open('s1_hex.txt', 'w') as f:
    f.write(s1_hex)

print(f"[+] Saved to s1_hex.txt")

# Try to submit
url = f"https://5bc1fecd4963fada.chal.ctf.ae/verify/{s1_hex}"
print(f"\n[+] Submitting to: {url[:80]}...")

response = requests.get(url)
print(f"[+] Response: {response.text}")

if 'flag' in response.text.lower():
    print(f"\n[+] FLAG FOUND!")
    print(response.text)

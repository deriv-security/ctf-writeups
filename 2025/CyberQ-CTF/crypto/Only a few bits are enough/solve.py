#!/usr/bin/env python3
import json
import hashlib
from fpylll import IntegerMatrix, LLL, BKZ
import subprocess

# Load the data
with open('public_data.json', 'r') as f:
    public_data = eval(f.read())

with open('leaked_data.json', 'r') as f:
    leaked_data = eval(f.read())

p = public_data['p']
g = public_data['g']
A = public_data['alice_responce']  # g^a
B = public_data['bob_responce']     # g^b

l = leaked_data['num_leaked_bits']  # 515 bits leaked
r1 = leaked_data['eva_forged_r1']
t0 = leaked_data['leaked_MSB_shared_secret']  # MSBs of g^(ab)
t1 = leaked_data['leaked_MSB_forged']         # MSBs of g^((a+r1)b)

print(f"[*] Prime p has {p.bit_length()} bits")
print(f"[*] Leaked {l} MSBs")
print(f"[*] g = {g}")
print(f"[*] A = g^a = {A}")
print(f"[*] B = g^b = {B}")

# The attack:
# We know:
# - s = g^(ab) mod p
# - s1 = g^((a+r1)b) mod p = g^(ab) * g^(r1*b) mod p = s * B^r1 mod p
# 
# We have MSBs of s and s1:
# s = t0 + u0 where u0 is unknown (509 bits)
# s1 = t1 + u1 where u1 is unknown (509 bits)
#
# From s1 = s * B^r1 mod p:
# t1 + u1 ≡ (t0 + u0) * B^r1 (mod p)
# t1 + u1 ≡ t0*B^r1 + u0*B^r1 (mod p)
# u1 - u0*B^r1 ≡ t0*B^r1 - t1 (mod p)

# Calculate B^r1 mod p
Br1 = pow(B, r1, p)

# Calculate the known part
known = (t0 * Br1 - t1) % p

# Number of unknown bits
unknown_bits = 1024 - l  # 509 bits

# We need to solve: u1 - u0*B^r1 ≡ known (mod p)
# where |u0|, |u1| < 2^unknown_bits

# Set up the lattice
# We'll use a 2D lattice with basis:
# [p,     0    ]
# [Br1,   2^k  ]
# where k is chosen to balance the lattice

# The target vector is approximately [known, 0]
# We're looking for a short vector [u1 - u0*Br1 - known, u0*2^k]
# which should be close to [0, u0*2^k]

print("\n[*] Setting up lattice attack...")

# Balance parameter - we want the two dimensions to be roughly equal
k = unknown_bits  # Scale factor

# Create the lattice basis
# Dimension: 2x2
M = IntegerMatrix(2, 2)
M[0, 0] = p
M[0, 1] = 0
M[1, 0] = Br1
M[1, 1] = 2**k

print(f"[*] Lattice dimension: 2x2")
print(f"[*] Scale factor k: {k}")

# Save matrix to file for flatter
with open('lattice_basis.txt', 'w') as f:
    f.write(f"2 2\n")
    f.write(f"{M[0, 0]} {M[0, 1]}\n")
    f.write(f"{M[1, 0]} {M[1, 1]}\n")

print("[*] Running flatter for lattice reduction...")
try:
    result = subprocess.run(['flatter', 'lattice_basis.txt'], 
                          capture_output=True, text=True, timeout=300)
    if result.returncode == 0:
        print("[+] Flatter completed successfully")
        # Parse flatter output
        lines = result.stdout.strip().split('\n')
        # Skip the dimension line
        reduced_basis = []
        for line in lines[1:]:
            if line.strip():
                reduced_basis.append([int(x) for x in line.split()])
        
        print(f"[*] Reduced basis vectors:")
        for i, vec in enumerate(reduced_basis):
            print(f"    v{i}: {vec}")
    else:
        print(f"[-] Flatter failed: {result.stderr}")
        print("[*] Falling back to BKZ reduction...")
        # Fallback to BKZ
        LLL.reduction(M)
        BKZ.reduction(M, BKZ.Param(block_size=20))
        reduced_basis = [[M[i, j] for j in range(2)] for i in range(2)]
except (subprocess.TimeoutExpired, FileNotFoundError) as e:
    print(f"[-] Flatter not available or timed out: {e}")
    print("[*] Using BKZ reduction...")
    LLL.reduction(M)
    BKZ.reduction(M, BKZ.Param(block_size=20))
    reduced_basis = [[M[i, j] for j in range(2)] for i in range(2)]

# Try to recover u0 from the short vectors
print("\n[*] Analyzing reduced basis vectors...")

candidates = []
for i, vec in enumerate(reduced_basis):
    v0, v1 = vec[0], vec[1]
    
    # From the short vector, extract u0
    # The vector should be approximately [u1 - u0*Br1 - known, u0*2^k]
    # So u0 ≈ v1 / 2^k
    
    if v1 != 0:
        u0_candidate = abs(v1) // (2**k)
        
        # Try both positive and negative
        for sign in [1, -1]:
            u0 = sign * u0_candidate
            
            # Check if u0 is in valid range
            if 0 <= u0 < 2**unknown_bits:
                # Calculate u1 from the relation
                u1 = (known + u0 * Br1) % p
                
                # Verify u1 is also in valid range
                if u1 < 2**unknown_bits:
                    # Reconstruct s
                    s = t0 + u0
                    
                    # Verify: s1 should equal s * B^r1 mod p
                    s1_check = (s * Br1) % p
                    s1_actual = t1 + u1
                    
                    if s1_check == s1_actual:
                        print(f"[+] Found valid candidate from vector {i}!")
                        print(f"    u0 = {u0}")
                        print(f"    u1 = {u1}")
                        candidates.append(s)

# Also try a direct approach: enumerate small values
print("\n[*] Trying direct enumeration approach...")
# Since we have 509 unknown bits, we can't enumerate all
# But the lattice should give us a good approximation

if not candidates:
    print("[-] No candidates found from lattice reduction")
    print("[*] Trying alternative approach...")
    
    # Alternative: use the fact that s^b = A (mod p)
    # We know MSBs of s, so we can try to find s by checking
    # if (t0 + u0)^b ≡ A (mod p) for small u0
    
    # This is still hard, but let's try a small range
    print("[*] Searching in small range around leaked MSBs...")
    for u0 in range(0, min(2**20, 2**unknown_bits)):  # Try first 2^20 values
        s_candidate = t0 + u0
        # Verify: B^a should equal s_candidate
        # We have A = g^a, B = g^b, s = g^(ab)
        # So s = A^b = B^a
        if pow(B, s_candidate, p) == pow(A, 1, p):  # This won't work directly
            candidates.append(s_candidate)
        
        if u0 % 100000 == 0:
            print(f"    Tried {u0} values...")
        
        if len(candidates) > 0:
            break

if candidates:
    print(f"\n[+] Found {len(candidates)} candidate(s)")
    
    for idx, s in enumerate(candidates):
        print(f"\n[*] Testing candidate {idx + 1}: {s}")
        
        # Convert to bytes and hash
        s_bytes = s.to_bytes(1024, "little")
        answer = hashlib.sha256(s_bytes).hexdigest()
        
        print(f"[*] SHA256 hash: {answer}")
        
        # Try to verify with the server
        print(f"[*] Verifying with server...")
        import requests
        try:
            url = f"https://b96c8dac547349e9.chal.ctf.ae/verify-secret/{answer}"
            response = requests.get(url, timeout=10)
            print(f"[*] Server response: {response.text}")
            
            if "flag" in response.text.lower() or "correct" in response.text.lower():
                print(f"\n[+] SUCCESS! Found the shared secret!")
                print(f"[+] Answer: {answer}")
                with open('answer.txt', 'w') as f:
                    f.write(answer)
                break
        except Exception as e:
            print(f"[-] Error verifying: {e}")
else:
    print("\n[-] No valid candidates found")
    print("[*] The lattice attack may need parameter tuning")

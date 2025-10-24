#!/usr/bin/env python3
"""
Schnorr Identification Protocol Attack

When the prover reuses the same commitment t in two different transcripts,
we can recover the secret key x.

Schnorr Protocol:
1. Prover chooses random r, computes t = g^r mod p
2. Verifier sends challenge c
3. Prover responds with z = r + c*x mod (p-1)
4. Verifier checks: g^z = t * y^c mod p

Attack:
Given two transcripts with same t but different c1, c2:
- z1 = r + c1*x mod (p-1)
- z2 = r + c2*x mod (p-1)

Subtracting:
z1 - z2 = (c1 - c2)*x mod (p-1)

Therefore:
x = (z1 - z2) * (c1 - c2)^(-1) mod (p-1)
"""

import json
import requests

# Load the data
with open("public_data.json", "r") as f:
    public_data = json.load(f)

with open("transcripts.json", "r") as f:
    transcripts_data = json.load(f)

p = int(public_data["public_prime"])
g = int(public_data["generator_g"])
y = int(public_data["public_y"])

transcripts = transcripts_data["transcripts"]
t1 = int(transcripts[0]["commitment_t"])
c1 = int(transcripts[0]["challenge_c"])
z1 = int(transcripts[0]["response_z"])

t2 = int(transcripts[1]["commitment_t"])
c2 = int(transcripts[1]["challenge_c"])
z2 = int(transcripts[1]["response_z"])

print("Public Parameters:")
print(f"p (prime): {p}")
print(f"g (generator): {g}")
print(f"y (public key): {y}")
print()

print("Transcript 1:")
print(f"t1: {t1}")
print(f"c1: {c1}")
print(f"z1: {z1}")
print()

print("Transcript 2:")
print(f"t2: {t2}")
print(f"c2: {c2}")
print(f"z2: {z2}")
print()

# Verify that t1 == t2 (same commitment reused)
assert t1 == t2, "Commitments should be the same!"
print("✓ Confirmed: Same commitment t used in both transcripts")
print()

# Attack: Recover secret key x
# z1 - z2 = (c1 - c2) * x mod (p-1)
# x = (z1 - z2) * (c1 - c2)^(-1) mod (p-1)

q = p - 1  # Order of the group
delta_z = (z1 - z2) % q
delta_c = (c1 - c2) % q

print(f"z1 - z2 mod (p-1): {delta_z}")
print(f"c1 - c2 mod (p-1): {delta_c}")
print()

# Compute modular inverse of (c1 - c2) mod (p-1)
delta_c_inv = pow(delta_c, -1, q)
print(f"(c1 - c2)^(-1) mod (p-1): {delta_c_inv}")
print()

# Recover secret key
x = (delta_z * delta_c_inv) % q
print(f"Recovered secret key x: {x}")
print()

# Verify the secret key is correct
# Check: y = g^x mod p
y_computed = pow(g, x, p)
print(f"Verification: g^x mod p = {y_computed}")
print(f"Expected y: {y}")
print(f"Match: {y_computed == y}")
print()

if y_computed == y:
    print("✓ Secret key recovered successfully!")
    print()
    
    # Now we can impersonate the prover
    # We need to:
    # 1. Send a commitment t = g^r mod p (choose random r)
    # 2. Receive challenge c
    # 3. Respond with z = r + c*x mod (p-1)
    
    print("="*80)
    print("Impersonating the prover to get the flag...")
    print("="*80)
    print()
    
    # Choose a random r (we'll use a simple value for demonstration)
    import random
    random.seed()
    r = random.randint(1, q-1)
    
    # Compute commitment
    t = pow(g, r, p)
    print(f"Chosen random r: {r}")
    print(f"Computed commitment t = g^r mod p: {t}")
    print()
    
    # Send commitment to get challenge
    base_url = "https://69437bcb00c84869.chal.ctf.ae"
    print(f"Sending commitment to {base_url}/get-challenge/{t}")
    response = requests.get(f"{base_url}/get-challenge/{t}")
    
    try:
        result = response.json()
        if "challenge" in result:
            c = int(result["challenge"])
            print(f"Received challenge c: {c}")
            print()
            
            # Compute response z = r + c*x mod (p-1)
            z = (r + c * x) % q
            print(f"Computed response z = r + c*x mod (p-1): {z}")
            print()
            
            # Send response to get flag
            print(f"Sending response to {base_url}/verify-response/{z}")
            response = requests.get(f"{base_url}/verify-response/{z}")
            
            print("Response:")
            print(response.text)
            
            # Try to extract flag
            if "flag{" in response.text:
                import re
                flag_match = re.search(r'flag\{[^}]+\}', response.text)
                if flag_match:
                    flag = flag_match.group(0)
                    print()
                    print("="*80)
                    print(f"FLAG FOUND: {flag}")
                    print("="*80)
                    
                    # Save flag
                    with open("flag.txt", "w") as f:
                        f.write(flag)
                    print("Flag saved to flag.txt")
        else:
            print(f"Unexpected response: {result}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Response text: {response.text}")
else:
    print("✗ Failed to recover secret key!")

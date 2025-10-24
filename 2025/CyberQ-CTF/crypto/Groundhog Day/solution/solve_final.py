#!/usr/bin/env python3
"""
Groundhog Day - AES-GCM Nonce Reuse Attack (Final Solution)

When AES-GCM reuses a nonce:
- C1 = P1 ⊕ Keystream
- C2 = P2 ⊕ Keystream
- Therefore: C1 ⊕ C2 = P1 ⊕ P2

The challenge:
- P1 is a JSON config with keys like "logLevel", "version", etc.
- P2 has the VALUES at the same character positions as the KEYS in P1
- By knowing the key names, we can recover the values and reconstruct both plaintexts
"""
import json
import requests

URL = "https://385ea9dd822ca807.chal.ctf.ae"

def xor_bytes(a, b):
    """XOR two byte strings"""
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    print("=" * 70)
    print("Groundhog Day - AES-GCM Nonce Reuse Attack")
    print("=" * 70)
    
    # Load challenge data
    with open("../challenge_data.json", "r") as f:
        challenge = json.load(f)
    
    with open("../crib.json", "r") as f:
        crib_data = json.load(f)
    
    c1 = bytes.fromhex(challenge["c1"])
    c2 = bytes.fromhex(challenge["c2"])
    keys = crib_data["keys"]
    fmt = crib_data["format"]
    
    print(f"\nCiphertext lengths: C1={len(c1)}, C2={len(c2)}")
    print(f"Known keys: {keys}")
    
    # XOR the ciphertexts to get P1 ⊕ P2
    xor_result = xor_bytes(c1, c2)
    
    # Build P1 structure carefully
    indent = " " * fmt["indent"]
    sep_comma = fmt["separators"][0]  # ", "
    sep_colon = fmt["separators"][1]  # ": "
    newline = fmt["newline"]
    
    print("\n" + "=" * 70)
    print("Step 1: Recover values from P2 by XORing with known keys in P1")
    print("=" * 70)
    
    # Start building P1
    p1_bytes = bytearray()
    p1_bytes.extend(b'{')
    p1_bytes.extend(newline.encode())
    pos = len(p1_bytes)
    
    recovered_values = {}
    
    # For each key, recover its corresponding value from P2
    for i, key in enumerate(keys):
        # Add indent
        p1_bytes.extend(indent.encode())
        pos += len(indent)
        
        # Add opening quote for key
        p1_bytes.extend(b'"')
        pos += 1
        
        # At this position, P1 has the key name, P2 has the value
        key_bytes = key.encode()
        key_start = pos
        key_end = pos + len(key_bytes)
        
        # Recover value: P2_value = (C1 ⊕ C2) ⊕ P1_key
        value_bytes = xor_bytes(xor_result[key_start:key_end], key_bytes)
        recovered_values[key] = value_bytes.decode('utf-8', errors='replace')
        print(f"  {key:12} -> '{recovered_values[key]}'")
        
        # Add key to P1
        p1_bytes.extend(key_bytes)
        pos += len(key_bytes)
        
        # Add closing quote, colon, space, opening quote for value
        p1_bytes.extend(b'"')
        p1_bytes.extend(sep_colon.encode())
        p1_bytes.extend(b'"')
        pos += 1 + len(sep_colon) + 1
        
        # Add the value we recovered
        p1_bytes.extend(value_bytes)
        pos += len(value_bytes)
        
        # Add closing quote for value
        p1_bytes.extend(b'"')
        pos += 1
        
        # Add comma if not the last key
        if i < len(keys) - 1:
            p1_bytes.extend(sep_comma.encode())
            pos += len(sep_comma)
        
        # Add newline
        p1_bytes.extend(newline.encode())
        pos += len(newline)
    
    # Add closing brace
    p1_bytes.extend(b'}')
    
    print("\n" + "=" * 70)
    print("Step 2: Reconstructed P1")
    print("=" * 70)
    p1_str = p1_bytes.decode('utf-8', errors='replace')
    print(p1_str)
    print(f"\nP1 length: {len(p1_bytes)} bytes")
    print(f"C1 length: {len(c1)} bytes")
    
    # Check if lengths match
    if len(p1_bytes) != len(c1):
        print(f"\nLength mismatch! P1={len(p1_bytes)}, C1={len(c1)}")
        print(f"Difference: {len(c1) - len(p1_bytes)} bytes")
        
        # The JSON might have a trailing newline
        if len(c1) - len(p1_bytes) == 1:
            print("Adding trailing newline to P1...")
            p1_bytes.extend(newline.encode())
        else:
            print("ERROR: Cannot determine correct P1 structure")
            return
    
    print("\n" + "=" * 70)
    print("Step 3: Compute keystream K = C1 ⊕ P1")
    print("=" * 70)
    
    keystream = xor_bytes(c1, p1_bytes)
    keystream_hex = keystream.hex()
    
    print(f"Keystream (first 100 hex chars): {keystream_hex[:100]}...")
    print(f"Keystream length: {len(keystream)} bytes")
    
    # Verify by decrypting C2
    print("\n" + "=" * 70)
    print("Step 4: Verify by recovering P2 = C2 ⊕ K")
    print("=" * 70)
    
    p2_recovered = xor_bytes(c2, keystream)
    p2_str = p2_recovered.decode('utf-8', errors='replace')
    print(p2_str[:500])
    
    # Submit keystream
    print("\n" + "=" * 70)
    print("Step 5: Submit keystream to server")
    print("=" * 70)
    
    try:
        response = requests.get(f"{URL}/submit-keystream/{keystream_hex}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
            
            if result.get("correct"):
                print("\n" + "=" * 70)
                print("SUCCESS! Flag obtained:")
                print("=" * 70)
                flag = result.get("flag", "No flag in response")
                print(flag)
                
                # Save flag
                with open("flag.txt", "w") as f:
                    f.write(flag + "\n")
                print("\nFlag saved to flag.txt")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

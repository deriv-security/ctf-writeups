#!/usr/bin/env python3
"""
Solve Groundhog Day - AES-GCM Nonce Reuse Attack (Final)

The P1 JSON has a trailing newline, making it 188 bytes total.
"""
import json
import requests

URL = "https://385ea9dd822ca807.chal.ctf.ae"

def xor_bytes(a, b):
    """XOR two byte strings"""
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    print("=" * 60)
    print("Groundhog Day - AES-GCM Nonce Reuse Attack (Final)")
    print("=" * 60)
    
    # Load challenge data
    with open("challenge_data.json", "r") as f:
        challenge = json.load(f)
    
    with open("crib.json", "r") as f:
        crib_data = json.load(f)
    
    c1 = bytes.fromhex(challenge["c1"])
    c2 = bytes.fromhex(challenge["c2"])
    keys = crib_data["keys"]
    fmt = crib_data["format"]
    
    print(f"\nCiphertext lengths: C1={len(c1)}, C2={len(c2)}")
    print(f"Known keys: {keys}")
    
    # XOR the ciphertexts
    xor_result = xor_bytes(c1, c2)
    
    # Build P1 structure
    indent = " " * fmt["indent"]
    sep_comma = fmt["separators"][0]
    sep_colon = fmt["separators"][1]
    newline = fmt["newline"]
    
    print("\n" + "=" * 60)
    print("Step 1: Recover values from P2")
    print("=" * 60)
    
    # Build P1 and track positions
    p1_bytes = bytearray()
    p1_bytes.extend(b'{\n')
    pos = 2
    
    recovered_values = {}
    
    # For each key, recover its value
    for i, key in enumerate(keys):
        # Add indent and opening quote
        p1_bytes.extend(indent.encode())
        pos += len(indent)
        p1_bytes.extend(b'"')
        pos += 1
        
        # At this position, P1 has the key name, P2 has the value
        key_bytes = key.encode()
        key_start = pos
        key_end = pos + len(key_bytes)
        
        # Recover value: P2_value = (C1 ⊕ C2) ⊕ P1_key
        value_bytes = xor_bytes(xor_result[key_start:key_end], key_bytes)
        recovered_values[key] = value_bytes.decode('utf-8', errors='replace')
        print(f"  {key:12} -> {recovered_values[key]}")
        
        p1_bytes.extend(key_bytes)
        pos += len(key_bytes)
        
        # Add quote, colon, space, quote
        p1_bytes.extend(b'": "')
        pos += 4
        
        # Now add the value we recovered
        p1_bytes.extend(value_bytes)
        pos += len(value_bytes)
        
        # Add closing quote
        p1_bytes.extend(b'"')
        pos += 1
        
        # Add comma and newline (except for last)
        if i < len(keys) - 1:
            p1_bytes.extend((sep_comma + newline).encode())
            pos += len(sep_comma) + len(newline)
    
    # Add closing with trailing newline
    p1_bytes.extend(b'\n}\n')
    
    print("\n" + "=" * 60)
    print("Step 2: Verify P1 reconstruction")
    print("=" * 60)
    print(f"P1 length: {len(p1_bytes)} bytes")
    print(p1_bytes.decode('utf-8', errors='replace'))
    
    if len(p1_bytes) != len(c1):
        print(f"\nERROR: P1 length ({len(p1_bytes)}) != C1 length ({len(c1)})")
        return
    
    # Compute keystream
    keystream = xor_bytes(c1, p1_bytes)
    keystream_hex = keystream.hex()
    
    print("\n" + "=" * 60)
    print("Step 3: Compute keystream")
    print("=" * 60)
    print(f"Keystream length: {len(keystream)} bytes")
    print(f"Keystream (hex): {keystream_hex}")
    
    # Verify by decrypting C2
    p2_recovered = xor_bytes(c2, keystream)
    print("\n" + "=" * 60)
    print("Step 4: Verify by recovering P2")
    print("=" * 60)
    print(p2_recovered.decode('utf-8', errors='replace'))
    
    # Submit keystream
    print("\n" + "=" * 60)
    print("Step 5: Submit keystream")
    print("=" * 60)
    
    try:
        response = requests.get(f"{URL}/submit-keystream/{keystream_hex}")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if result.get("correct"):
            print("\n" + "=" * 60)
            print("SUCCESS! Flag obtained:")
            print("=" * 60)
            flag = result.get("flag", "No flag in response")
            print(flag)
            
            # Save flag
            with open("flag.txt", "w") as f:
                f.write(flag + "\n")
            print("\nFlag saved to flag.txt")
        else:
            print("\nFailed to get flag. Reason:", result.get("reason", "unknown"))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

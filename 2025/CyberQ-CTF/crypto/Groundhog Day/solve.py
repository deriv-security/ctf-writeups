#!/usr/bin/env python3
"""
Solve Groundhog Day - AES-GCM Nonce Reuse Attack

The attack exploits the fact that when the same nonce is reused with AES-GCM:
C1 = P1 ⊕ K
C2 = P2 ⊕ K

Therefore: C1 ⊕ C2 = P1 ⊕ P2

P1 is a JSON config with keys like "logLevel", "version", etc.
P2 has the VALUES at the same positions as the KEYS in P1.

By knowing the key names, we can:
1. XOR C1 and C2 to get P1 ⊕ P2
2. At key positions, we know P1 (the key name), so we can recover P2 (the value)
3. At value positions in P1, we know P2 (from step 2), so we can recover P1 (the value)
4. Reconstruct full P1, then compute K = C1 ⊕ P1
"""
import json
import requests

URL = "https://385ea9dd822ca807.chal.ctf.ae"

def xor_bytes(a, b):
    """XOR two byte strings"""
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    print("=" * 60)
    print("Groundhog Day - AES-GCM Nonce Reuse Attack")
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
    print(f"Format: indent={fmt['indent']}, separators={fmt['separators']}")
    
    # XOR the ciphertexts to get P1 ⊕ P2
    xor_result = xor_bytes(c1, c2)
    print(f"\nC1 ⊕ C2 length: {len(xor_result)}")
    
    # Build the expected JSON structure for P1
    # Format: {"key1": "value1", "key2": "value2", ...}
    indent = " " * fmt["indent"]
    sep_comma = fmt["separators"][0]  # ", "
    sep_colon = fmt["separators"][1]  # ": "
    newline = fmt["newline"]
    
    # We need to figure out the structure by analyzing the XOR
    # Let's try to find key positions and extract values
    
    print("\n" + "=" * 60)
    print("Analyzing XOR to find key-value pairs...")
    print("=" * 60)
    
    # Convert to string to analyze (some bytes might not be printable)
    # We'll work byte by byte
    
    # Strategy: Build P1 incrementally
    # Start with opening brace
    p1_parts = ["{", newline]
    
    # For each key, we need to find where it appears in P1
    # The structure is: {"key1": "value1", "key2": "value2", ...}
    
    recovered_values = {}
    
    # Let's try a different approach: search for key patterns in the XOR
    # When we XOR "key" in P1 with "val" in P2, we get "key" ⊕ "val"
    # We can try each key and see if we can find a reasonable value
    
    for i, key in enumerate(keys):
        print(f"\nProcessing key: {key}")
        
        # Build the expected line format
        if i == 0:
            line_prefix = indent + '"' + key + '"' + sep_colon + '"'
        else:
            line_prefix = sep_comma + newline + indent + '"' + key + '"' + sep_colon + '"'
        
        # Search for this pattern in P1
        # We need to find where this key appears
        # Let's try to match by looking at the XOR pattern
        
        # For now, let's assume a simple structure and try to extract values
        # by XORing at expected positions
    
    # Alternative approach: Let's reconstruct P1 by assuming standard JSON format
    # and using the XOR to recover values
    
    print("\n" + "=" * 60)
    print("Attempting to recover plaintext structure...")
    print("=" * 60)
    
    # Let's try to build P1 character by character using the XOR
    # We know P1 is JSON, so we can make educated guesses
    
    # Start with what we know: P1 begins with "{\n"
    p1_bytes = bytearray()
    p2_bytes = bytearray()
    
    # Opening brace and newline
    p1_bytes.extend(b'{\n')
    p2_bytes.extend(xor_bytes(c1[:2], b'{\n'))
    
    pos = 2
    
    # For each key
    for i, key in enumerate(keys):
        # Add indent
        p1_bytes.extend(indent.encode())
        p2_bytes.extend(xor_bytes(c1[pos:pos+len(indent)], indent.encode()))
        pos += len(indent)
        
        # Add opening quote for key
        p1_bytes.extend(b'"')
        p2_bytes.extend(xor_bytes(c1[pos:pos+1], b'"'))
        pos += 1
        
        # Add key name
        key_bytes = key.encode()
        p1_bytes.extend(key_bytes)
        # At this position in P2, we have the VALUE (same length as key)
        value_bytes = xor_bytes(c1[pos:pos+len(key_bytes)], key_bytes)
        value_bytes = xor_bytes(value_bytes, xor_result[pos:pos+len(key_bytes)])
        p2_bytes.extend(value_bytes)
        recovered_values[key] = value_bytes.decode('utf-8', errors='replace')
        print(f"  {key} -> {recovered_values[key]}")
        pos += len(key_bytes)
        
        # Add closing quote, colon, space, opening quote for value
        p1_bytes.extend(b'": "')
        p2_bytes.extend(xor_bytes(c1[pos:pos+4], b'": "'))
        pos += 4
        
        # Add value (we recovered this from P2)
        value_bytes = recovered_values[key].encode()
        p1_bytes.extend(value_bytes)
        # At this position in P2, we have filler (probably spaces or specific chars)
        p2_filler = xor_bytes(c1[pos:pos+len(value_bytes)], value_bytes)
        p2_bytes.extend(p2_filler)
        pos += len(value_bytes)
        
        # Add closing quote
        p1_bytes.extend(b'"')
        p2_bytes.extend(xor_bytes(c1[pos:pos+1], b'"'))
        pos += 1
        
        # Add comma and newline (except for last key)
        if i < len(keys) - 1:
            p1_bytes.extend(sep_comma.encode() + newline.encode())
            p2_bytes.extend(xor_bytes(c1[pos:pos+len(sep_comma)+len(newline)], 
                                     (sep_comma + newline).encode()))
            pos += len(sep_comma) + len(newline)
    
    # Add closing newline and brace
    p1_bytes.extend(b'\n}')
    p2_bytes.extend(xor_bytes(c1[pos:pos+2], b'\n}'))
    pos += 2
    
    print("\n" + "=" * 60)
    print("Recovered P1 (first 500 chars):")
    print("=" * 60)
    print(p1_bytes[:500].decode('utf-8', errors='replace'))
    
    # Compute keystream
    keystream = xor_bytes(c1[:len(p1_bytes)], p1_bytes)
    keystream_hex = keystream.hex()
    
    print("\n" + "=" * 60)
    print(f"Keystream (first 100 chars): {keystream_hex[:100]}")
    print(f"Keystream length: {len(keystream)} bytes")
    print("=" * 60)
    
    # If we have the full plaintext length, extend keystream
    if len(p1_bytes) < len(c1):
        print(f"\nWarning: P1 length ({len(p1_bytes)}) < C1 length ({len(c1)})")
        print("Need to recover more of P1 to get full keystream")
    
    # Submit keystream
    print("\n" + "=" * 60)
    print("Submitting keystream...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{URL}/submit-keystream/{keystream_hex}")
        print(f"Status: {response.status_code}")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

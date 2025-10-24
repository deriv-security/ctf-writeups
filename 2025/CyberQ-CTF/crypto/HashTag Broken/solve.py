#!/usr/bin/env python3
"""
HashTag: Broken - Hash Collision Challenge
==========================================

The challenge uses a weak hash function that computes:
    hash(s) = sum(ord(c) for c in s) % 512

This is trivially breakable because we only need to match modulo 512.

Strategy:
---------
Given: "The_winner_of_the_prize_is_IGOR"
Goal: Create "The_winner_of_the_prize_is_<NEW_NAME>" with same hash

We calculate the target hash for the new name and find a combination
of characters that produces that hash.
"""

import requests

def sum_ascii_hash(s: str) -> int:
    """Compute the sum of ASCII values of all characters modulo 512."""
    return sum(ord(c) for c in s) % 512

def find_collision(original_message: str, base_url: str):
    """Find a collision for the weak hash function."""
    print("=" * 70)
    print("HashTag: Broken - Hash Collision Exploit")
    print("=" * 70)
    
    # Calculate original hash
    original_hash = sum_ascii_hash(original_message)
    print(f"\nOriginal message: {original_message}")
    print(f"Original hash: {original_hash}")
    
    # Extract the prefix and original name
    prefix = "The_winner_of_the_prize_is_"
    original_name = original_message[len(prefix):]
    print(f"Original name: {original_name}")
    
    # Calculate what hash the new name needs to have
    prefix_hash = sum_ascii_hash(prefix)
    target_name_hash = (original_hash - prefix_hash) % 512
    
    print(f"\nPrefix hash: {prefix_hash}")
    print(f"Target name hash (mod 512): {target_name_hash}")
    
    print("\n" + "=" * 70)
    print("Finding collision...")
    print("=" * 70)
    
    # Try different base names and add characters to match the target
    test_names = ["ALICE", "BOB", "CHARLIE", "DAVE", "EVE", "FRANK", "GRACE", "HACKER"]
    
    new_name = None
    for base_name in test_names:
        base_hash = sum_ascii_hash(base_name)
        needed = (target_name_hash - base_hash) % 512
        
        print(f"\n{base_name}: hash = {base_hash}, need to add: {needed}")
        
        if needed == 0:
            new_name = base_name
            print(f"  Perfect match!")
            break
        
        # Try adding characters to reach the target
        # We'll use lowercase letters and underscores
        for char in "abcdefghijklmnopqrstuvwxyz_":
            char_val = ord(char)
            # How many of this character do we need?
            count = needed // char_val
            remainder = needed % char_val
            
            if remainder == 0 and count > 0 and count < 20:
                # Found a solution
                new_name = base_name + char * count
                print(f"  Found: {new_name} (added {count} '{char}')")
                break
            
            # Try combinations with another character
            for char2 in "abcdefghijklmnopqrstuvwxyz_":
                char2_val = ord(char2)
                for c1 in range(1, 10):
                    for c2 in range(1, 10):
                        if c1 * char_val + c2 * char2_val == needed:
                            new_name = base_name + char * c1 + char2 * c2
                            print(f"  Found: {new_name}")
                            break
                    if new_name:
                        break
                if new_name:
                    break
        
        if new_name:
            break
    
    # If we still haven't found one, use a brute force approach
    if not new_name:
        print("\nUsing brute force approach...")
        base_name = "ALICE"
        base_hash = sum_ascii_hash(base_name)
        needed = (target_name_hash - base_hash) % 512
        
        # Just add 'a' characters (ASCII 97)
        # We might need to add a combination
        num_a = needed // 97
        remainder = needed % 97
        
        if remainder == 0:
            new_name = base_name + 'a' * num_a
        else:
            # Add 'a's and then find the right character for remainder
            new_name = base_name + 'a' * num_a + chr(remainder)
    
    # Verify the collision
    new_message = prefix + new_name
    new_hash = sum_ascii_hash(new_message)
    
    print("\n" + "=" * 70)
    print("Verification")
    print("=" * 70)
    print(f"New message: {new_message}")
    print(f"New hash: {new_hash}")
    print(f"Original hash: {original_hash}")
    print(f"Match: {new_hash == original_hash}")
    
    if new_hash == original_hash:
        print("\n" + "=" * 70)
        print("Submitting to server...")
        print("=" * 70)
        
        # Submit to server
        verify_url = f"{base_url}/verify/{new_message}"
        response = requests.get(verify_url)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n" + "=" * 70)
            print("SUCCESS!")
            print("=" * 70)
            
            # Save flag if present
            if "flag{" in response.text:
                with open("flag.txt", "w") as f:
                    f.write(response.text)
                print("Flag saved to flag.txt")
            
            return response.text
    
    return None

if __name__ == "__main__":
    base_url = "https://480a8476a130f2a6.chal.ctf.ae"
    
    # Read original message
    with open("original_message.txt", "r") as f:
        original_message = f.read().strip()
    
    result = find_collision(original_message, base_url)
    
    if result:
        print(f"\nResult: {result}")

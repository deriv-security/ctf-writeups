# Sign and Run

**Category:** Cryptography  
**Difficulty:** Medium  
**Points:** 300  
**Flag:** `HTB{w3_sh0u1d_m3333333t_1n_th3_m1dd13!!!!!_05db84ac65ffabceaf29af656601abfc}`

## Challenge Description

At the edge of Hollow Mere stands an ancient automaton known as the Iron Scribe - a machine that writes commands in living metal and executes only those sealed with a valid mark. The Scribe's master key was lost ages ago, but its forges still hum, stamping glyphs of permission into every order it receives. Willem approaches the machine's console, where it offers a bargain: "Sign your words, and I shall act. Present a forged seal, and be undone." To awaken the Scribe's obedience, one must understand how its mark is made... and how to make it lie.

**Connection:** `nc 64.226.81.188 32003`

## Overview

This challenge presents an RSA-based command execution system with a flawed signature scheme. The server allows users to:
1. Request signatures for commands (`inscribe`)
2. Execute commands with valid signatures (`invoke`)

The vulnerability lies in using CRC32 (32-bit) for signatures, making them susceptible to a meet-in-the-middle attack.

## Vulnerability Analysis

### Signature Scheme

The server implements the following signature process:

```python
def helper_sig(cmd):
    pt = bytes_to_long(cmd.encode())
    ct = pow(pt, d, N)  # RSA encryption with private key
    return crc32(long_to_bytes(ct))  # CRC32 of encrypted command

def sign_command(cmd):
    sig = helper_sig(cmd)
    print(f"Encrypted signature: {pow(sig, e, N)}")  # Encrypt the signature
```

**The Critical Flaw:** CRC32 produces only 32-bit values (2^32 possible signatures), making the signature space extremely small and vulnerable to brute force attacks.

### Attack Strategy: Meet-in-the-Middle

Instead of brute forcing all 2^32 signatures, we can reduce the search space to 2^16 using a meet-in-the-middle approach:

1. **Mathematical Foundation:**
   - We need to find `sig` such that `sig^e ≡ encrypted_sig (mod N)`
   - If we write `sig = h1 * h2` where `h1, h2 < 2^16`, then:
   - `(h1 * h2)^e ≡ encrypted_sig (mod N)`
   - This gives us: `h1^e * h2^e ≡ encrypted_sig (mod N)`
   - Rearranging: `h1^e ≡ encrypted_sig * (h2^e)^-1 (mod N)`

2. **Implementation:**
   - **Baby Steps:** Build a table of `h1^e mod N` for `h1 ∈ [1, 2^16)`
   - **Giant Steps:** For each `h2 ∈ [1, 2^16)`, compute `target = encrypted_sig * (h2^e)^-1 mod N`
   - **Collision:** If `target` exists in our baby steps table, then `sig = h1 * h2`

This reduces the complexity from O(2^32) to O(2^16), making the attack practical.

## Solution

The exploit script performs the following steps:

1. **Connect and Parse:** Extract RSA parameters (N, e) from the server
2. **Request Signature:** Use `inscribe` command to get an encrypted signature for our target command
3. **Meet-in-the-Middle Attack:** Find the 32-bit signature value
4. **Execute Command:** Use `invoke` with the forged signature to execute our command

### Key Code Snippet

```python
def find_seal(N, e, enc_seal):
    m = 2**16
    babies = {}
    
    # Baby Steps: Build lookup table
    for h1 in range(1, m):
        val = pow(h1, e, N)
        babies[val] = h1
    
    # Giant Steps: Search for collision
    for h2 in range(1, m):
        h2_pow_e_inv = inverse(pow(h2, e, N), N)
        target = (enc_seal * h2_pow_e_inv) % N
        
        if target in babies:
            h1 = babies[target]
            return h1 * h2
    
    return None
```

## Running the Exploit

```bash
python solve.py
```

The script will:
1. Connect to the challenge server
2. Request a signature for `cat${IFS}flag.txt`
3. Perform the meet-in-the-middle attack
4. Execute the command with the forged signature
5. Display the flag

**Note:** The attack may require multiple attempts since not all 32-bit signatures are (2^16)-smooth. The script automatically retries until successful.

## Files

- `server.py` - Challenge server implementation
- `solve.py` - Complete exploit script with meet-in-the-middle attack

## Flag

```
HTB{w3_sh0u1d_m3333333t_1n_th3_m1dd13!!!!!_05db84ac65ffabceaf29af656601abfc}
```

## Key Takeaways

1. **Weak Signature Space:** Using CRC32 (32-bit) for cryptographic signatures is insecure
2. **Meet-in-the-Middle:** An effective technique for reducing brute force complexity
3. **Proper Cryptography:** Always use cryptographically secure signature schemes (e.g., RSA-PSS, ECDSA)

The flag message "w3_sh0u1d_m3333333t_1n_th3_m1dd13!!!!!" cleverly references the meet-in-the-middle attack technique used to solve this challenge.

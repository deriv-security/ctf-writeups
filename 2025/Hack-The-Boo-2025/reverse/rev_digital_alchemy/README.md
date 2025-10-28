# Digital Alchemy

**Challenge Name:** Digital Alchemy  
**Category:** Reverse Engineering  
**Difficulty:** Medium  
**Points:** TBD

## Challenge Description

> In the depths of the Hollowed Forge, a relic of forgotten craft awaits—the Athanor, a vessel said to transmute shadow into light. Elin approaches its iron gates, clutching fragments of old alchemical texts. With careful incantation and precise timing, she coaxes the apparatus to life. The Athanor hums, consuming darkness, and from its core, a single golden thread emerges—proof that even in cursed lands, transformation is possible.

## Challenge Overview

The binary `athanor` implements a digital "alchemist" that processes `lead.txt` to produce `gold.txt` containing the flag. The program includes anti-debugging time checks and implementation bugs that must be bypassed to successfully extract the flag.

## Initial Analysis

### Binary Analysis

```bash
file athanor
# ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked

strings athanor | grep -E "(lead|gold|MTRLLEAD|USMWO|Initializing|Incantation)"
# MTRLLEAD
# USMWO[]\iN[QWRYdqXle[i_bm^aoc
# lead.txt
# gold.txt
# Initializing the Athanor...
# Incantation mismatch...
# The Athanor glows brightly...
```

### lead.txt File Structure

```
Offset  Description
0-7     Magic header: "MTRLLEAD"
8-11    4-byte big-endian state seed (0x972cffbc)
12-40   29-byte incantation data
41-47   7-byte encrypted secret
48-74   26-byte encrypted flag data
```

## Algorithm Reconstruction

### 1. Header Validation

The binary reads `lead.txt` in binary mode and performs initial validation:
- Verifies 8-byte magic header "MTRLLEAD"
- Extracts 4-byte big-endian state variable: `var_e8 = 0x972cffbc`

### 2. Anti-Debugging Time Checks

The binary includes two time checks that affect critical variables:

```c
// First time check - affects var_f4
if (time_diff > 2) var_f4 = 0xdead;
else var_f4 = 0x214f;  // Correct value needed for LCG

// Second time check - affects var_10
if (time_diff > 2) var_10 = 0xdead;
else var_10 = sum_of_incantation_bytes;  // Correct value needed
```

When running under a debugger or with delays, the program sets fail values (`0xdead`) instead of the correct values needed for decryption.

### 3. Incantation Decoding (First Transform)

Target string: `USMWO[]\iN[QWRYdqXle[i_bm^aoc` (29 bytes)

For each byte i in 0..28:
```c
byte var_51 = 0x40;  // '@'
var_8f = (var_51 + i) & 0xff;
var_8e = ((input_byte + var_8f) ^ var_51) & 0xff;
result = (var_8e % 127) + 1;
var_10 += input_byte;  // Accumulate sum for later use
```

### 4. Secret Decryption (LCG-based XOR)

The main decryption uses a Linear Congruential Generator (LCG):

```c
// LCG parameters
const uint32_t MODULUS = 0x26688d;
const uint32_t MULTIPLIER = 0x214f;  // var_f4 (anti-debug bypass needed)
const uint32_t INCREMENT = var_10;    // Sum from incantation

// State update (critical: 32-bit arithmetic!)
state = ((MULTIPLIER * state) + INCREMENT) % MODULUS;

// XOR with lower 4 bits
output_byte = input_byte ^ (state & 0xf);
```

## Implementation Bugs Fixed

### Bug 1: Off-by-One Error

The binary allocates 40 bytes for the encrypted payload but only processes 7 bytes using `size-1`. To extract the complete flag, we need to process all 33 bytes of the encrypted data.

**Fix:** Process the entire encrypted payload (33 bytes total) instead of just 7 bytes.

### Bug 2: 32-bit Arithmetic Overflow

The LCG state updates must use 32-bit arithmetic before the modulo operation to match the binary's behavior.

**Fix:** Ensure all multiplication operations are masked to 32-bit: `(a * b) & 0xffffffff` before applying modulo.

## Solution

```python
#!/usr/bin/env python3
"""
Digital Alchemy Solver
Decrypts lead.txt to extract the flag from gold.txt
"""

def decrypt_lead():
    """
    Decrypt the lead.txt file using reversed LCG algorithm
    """
    with open('lead.txt', 'rb') as f:
        data = f.read()

    # Validate header
    assert data.startswith(b'MTRLLEAD'), "Invalid magic header"

    # Extract initial state (big-endian)
    ptr = 8
    state = int.from_bytes(data[ptr:ptr+4], 'big') & 0xffffffff
    ptr += 4

    # Process incantation data to calculate var_10
    first_len = 29
    var_10 = sum(data[ptr:ptr+first_len]) & 0xffffffff
    ptr += first_len

    # Decrypt remaining data (33 bytes total)
    encrypted = data[ptr:]
    result = bytearray()

    for byte_val in encrypted:
        # LCG state update (32-bit arithmetic)
        state = ((0x214f * (state & 0xffffffff)) & 0xffffffff)
        state = (state + (var_10 & 0xffffffff)) & 0xffffffff
        state = state % 0x26688d  # Modulo after 32-bit multiplication

        # XOR with lower 4 bits
        result.append(byte_val ^ (state & 0xf))

    # Decode and clean up output
    return bytes(result).decode('latin-1').rstrip('\x0c')

if __name__ == "__main__":
    flag = decrypt_lead()
    print(f"HTB{{{flag}}}")
    
    # Write to gold.txt for verification
    with open('gold.txt', 'w') as f:
        f.write(f"HTB{{{flag}}}")
```

## Running the Solution

```bash
# Run the Python solver
python3 solve.py

# Verify with the binary (requires Linux/Docker)
docker run --rm --platform=linux/amd64 \
  -v "$(pwd)":/chal -w /chal \
  ubuntu:22.04 bash -lc "./athanor && cat gold.txt"
```

## Key Technical Insights

1. **32-bit Arithmetic:** Critical for LCG state transitions - all operations must be masked to 32-bit before modulo
2. **Anti-Debug Bypass:** Use correct values (0x214f, calculated sum) not fail values (0xdead)
3. **Complete Payload Processing:** Process entire 33-byte encrypted section, not just 7 bytes
4. **Latin-1 Decoding:** Handle non-ASCII characters in flag output

## Tools Used

- **radare2** - Binary analysis and disassembly
- **Docker** - Linux environment for ELF execution
- **Python 3** - Algorithm implementation and verification
- **hexdump** - Data structure analysis

## Flag

```
HTB{Sp1r1t_0f_Th3_C0d3_Aw4k3n3d}

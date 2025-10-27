#!/usr/bin/env python3
from pwn import *
import ssl

# Connect to the server
host = "bdb38af256756430.chal.ctf.ae"
port = 443

# Try with SSL
context.log_level = 'debug'
conn = remote(host, port, ssl=True, sni=host)

# Receive all data
try:
    data = conn.recvall(timeout=5).decode()
    print("Received data:")
    print(data)
except Exception as e:
    print(f"Error: {e}")
    # Try to receive line by line
    try:
        while True:
            line = conn.recvline(timeout=2).decode()
            print(line)
    except:
        pass

conn.close()

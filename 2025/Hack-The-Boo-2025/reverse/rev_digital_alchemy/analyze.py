#!/usr/bin/env python3
"""
Analysis of the Digital Alchemy challenge.

Looking at the disassembly more carefully:
- There are time checks that modify var_f4 and var_10
- var_f4 starts as 0x214f but becomes 0xdead if time check fails
- var_10 is calculated as sum but becomes 0xdead if time check fails

The challenge says "fix his amateur mistakes" - maybe the bug is that
we need to figure out what the CORRECT values should be?

Let's examine the lead.txt more carefully.
"""

with open('lead.txt', 'rb') as f:
    data = f.read()

print("Full data hex:")
print(data.hex())
print()

print("Data breakdown:")
print(f"Header (8 bytes): {data[0:8]} = {data[0:8].hex()}")
print(f"var_e8 (4 bytes): {data[8:12].hex()} = 0x{data[8] << 24 | data[9] << 16 | data[10] << 8 | data[11]:08x}")
print(f"Incantation data: {data[12:41]}")
print(f"Secret data: {data[41:48]}")
print(f"Remaining: {data[48:]}")
print()

# The incantation text in the data
incantation_text = data[12:41]
print(f"Incantation text: {incantation_text}")
print(f"Length: {len(incantation_text)}")

# Check what the text says
print()
print("The incantation appears to be: SPIRITUS_CODICIS_EXPERGISCEREM")
print("This is Latin - it could mean something like 'Spirit of the Code Awakens'")
print()

# The data after that
remaining = data[41:]
print(f"Data after incantation: {remaining}")
print(f"Hex: {remaining.hex()}")
print(f"Length: {len(remaining)}")


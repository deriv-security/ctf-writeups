#!/usr/bin/env python3

# Encrypted data from obj.enc (24 qwords in little-endian)
enc_data = [
    0x000000000000fffe,
    0x000000000000ff8e,
    0x000000000000ffd6,
    0x000000000000ff32,
    0x000000000000ff12,
    0x000000000000ff72,
    0x000000000000fe1a,
    0x000000000000ff1e,
    0x000000000000ff9e,
    0x000000000000fe1a,
    0x000000000000ff66,
    0x000000000000ffc2,
    0x000000000000fe6a,
    0x000000000000ffd2,
    0x000000000000fe0e,
    0x000000000000ff6e,
    0x000000000000ff6e,
    0x000000000000fe4e,
    0x000000000000fe5a,
    0x000000000000fe5a,
    0x000000000000fe1a,
    0x000000000000fe5a,
    0x000000000000ff2a,
    0x0000000000000000,
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


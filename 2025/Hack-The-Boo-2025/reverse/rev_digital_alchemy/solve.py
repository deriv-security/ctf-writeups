from pathlib import Path
raw = Path('/Users/test3/practice/reversing-htb/rev_digital_alchemy/lead.txt').read_bytes()
assert raw.startswith(b'MTRLLEAD')
ptr=8
state = int.from_bytes(raw[ptr:ptr+4],'big') & 0xffffffff
ptr += 4
# First loop to get sum and length (length is 29)
L=29
sumv = sum(raw[ptr:ptr+L]) & 0xffffffff
ptr += L
enc_full = raw[ptr:]
enc7 = enc_full[:7]
A_good = 0x214f
M = 0x26688d
# function to iterate

def decrypt(enc, A, C):
    s = state
    out = bytearray()
    for b in enc:
        s = ((A * (s & 0xffffffff)) & 0xffffffff)
        s = (s + (C & 0xffffffff)) & 0xffffffff
        s = divmod(s, M)[1]  # remainder in 32-bit division
        out.append(b ^ (s & 0xf))
    return bytes(out)

print('7-bytes correct32:', decrypt(enc7, A_good, sumv))
print('full correct32:', decrypt(enc_full, A_good, sumv))
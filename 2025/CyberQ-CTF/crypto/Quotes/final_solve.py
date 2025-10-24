#!/usr/bin/env python3
"""
Final solver with correct mapping
"""

# Current ciphertext from last connection
ct = "izwekes, lu we bz bljtzkes h tzxvoede diezsf, ld jiznob lc dlxe ge ncbesjdhcbhgoe lc gszhb vslctlvoe gf ekesfzce, czd anjd h uew jtlecdljdj. diec we jihoo hoo, vilozjzviesj, jtlecdljdj, hcb anjd zsblchsf vezvoe, ge hgoe dz dhqe vhsd lc die bljtnjjlzc zu die mnejdlzc zu wif ld lj dihd we hcb die nclkesje erljd. lu we ulcb die hcjwes dz dihd, ld wznob ge die nodlxhde dslnxvi zu inxhc sehjzc  uzs diec we wznob qczw die xlcb zu yzb."

# Correct mapping based on patterns
# die = the: d=t, i=h, e=e
# we = we: w=w, e=e (confirmed)
# lu = if: l=i, u=f
# bz = do: b=d, z=o
# lc = in: l=i (confirmed), c=n
# ge = be: g=b, e=e (confirmed)
# zu = of: z=o (confirmed), u=f (confirmed)
# ld = it: l=i (confirmed), d=t (confirmed)
# jiznob = should: j=s, i=h (confirmed), z=o (confirmed), n=u, o=l, b=d (confirmed)
# dz = to: d=t (confirmed), z=o (confirmed)

mapping = {
    'd': 't', 'i': 'h', 'e': 'e',
    'w': 'w', 'l': 'i', 'u': 'f',
    'b': 'd', 'z': 'o', 'c': 'n',
    'g': 'b', 'j': 's', 'n': 'u',
    'o': 'l', 's': 'r', 'v': 'p',
    'k': 'v', 'f': 'y', 'h': 'a',
    'q': 'k', 'x': 'm', 't': 'c',
    'a': 'j', 'p': 'g', 'y': 'g',
    'm': 'q', 'r': 'x'
}

plaintext = ""
for char in ct.lower():
    if char in mapping:
        plaintext += mapping[char]
    else:
        plaintext += char

print("[*] Decrypted text:")
print(plaintext)
print("\n[*] This is from Stephen Hawking's 'A Brief History of Time'!")
print("\n[*] Plaintext to submit:")
print(plaintext)

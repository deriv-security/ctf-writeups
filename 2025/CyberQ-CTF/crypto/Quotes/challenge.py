import random
import string
import os
from secr3ts import quotes

FLAG = os.environ.get('FLAG', b'flag{d6d35ea56db4ce1}')
def encrypt(plaintext):
    alphabet = list(string.ascii_lowercase)
    shuffled_alphabet = list(string.ascii_lowercase)
    random.shuffle(shuffled_alphabet)
    key = dict(zip(alphabet, shuffled_alphabet))
    ciphertext = ""
    for char in plaintext:
        if char in key:
             ciphertext += key[char]
        else:
            ciphertext += char
            
    return ciphertext, key






pt=random.choice(quotes).lower()

ct=encrypt(pt)


banner="""========================================
   SUBSTITUTION CIPHER ENCRYPTOR
========================================"""
ct=ct[0]
print(banner)
print(f"{ct = }")

print(" can you guess my pt ;) ?")
pt2= input("pt = ")
if pt2==pt:
	print("here is your flag ",FLAG)
else:
	print('wrong text no flag for you ')






from Crypto.Util.number import getPrime, inverse, long_to_bytes,bytes_to_long
import math
import os
from Crypto.Cipher import AES
from base64 import b64encode
from Crypto.Util.Padding import pad,unpad

key=os.urandom(16)
iv=os.urandom(16)
FLAG = os.environ.get('FLAG', b'flag{d6d35ea56db4ce1}')

def encrypt(pt):
	cipher=AES.new(key,AES.MODE_OFB,iv)
	ct=cipher.encrypt(pad(pt,16))
	return ct

print('here is my secret can u recover it :')
enc=encrypt(FLAG.encode())
print(f"{enc.hex() = }")
while True:
	pt=input("what text do you want to encrypt->").encode()
	ct=encrypt(pt)
	print(f'{ct.hex() = }')
	




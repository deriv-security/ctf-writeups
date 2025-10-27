from ecdsa.ecdsa import generator_256, Public_key, Private_key
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
from random import randint
from hashlib import sha256
import os
import json
FLAG = os.environ.get('FLAG', 'flag{506f6c796d65726f5761734865726521}')
if isinstance(FLAG, str):
    FLAG = FLAG.encode()
G = generator_256
q = G.order()
d = randint(1, q-1)
pubkey = Public_key(G, d*G)
privkey = Private_key(pubkey, d)


def ecdsa_sign(msg, privkey):
    h = int(sha256(msg.encode()).hexdigest(), 16)
    nonce = ((h // 2**128) * 2**128) + d
    sig = privkey.sign(h, nonce)
    return json.dumps({'msg': msg, 'r': int(sig.r), 's': int(sig.s)})

def encrypt_flag(msg):
    key = sha256(str(d).encode()).digest()[:16]
    aes = AES.new(key, AES.MODE_ECB)
    return aes.encrypt(pad(msg, 16)).hex()


if __name__ == '__main__':
    sig = ecdsa_sign('Stay at home kiddo !', privkey)
    enc_flag = encrypt_flag(FLAG)

    print(f'{sig = }')
    print(f'{enc_flag = }')

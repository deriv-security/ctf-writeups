# Quotes Challenge - Solution

## Challenge Overview

**Category:** Cryptography  
**Difficulty:** Easy  
**Points:** 490  
**Instance:** 06ff952ba10502bc.chal.ctf.ae:443

## Challenge Description

The challenge presents a substitution cipher where:
1. A random quote is selected from a hidden list
2. Each letter is randomly mapped to another letter
3. The ciphertext is displayed
4. You must guess the original plaintext to get the flag

## Key Insight

Each connection to the server generates a **different random quote** with a **different random substitution cipher**. This means:
- You cannot reuse previous solutions
- You must decrypt each ciphertext independently
- The quotes appear to be famous historical quotes

## Solution Approach

### Method 1: Manual Frequency Analysis (Used Successfully)

For the first ciphertext, I used frequency analysis:

**Ciphertext:**
```
le ly pte emn valelv rmt vtkpey; pte emn bcp rmt jtlpey tke mtr emn yeatpd bcp yekbfqny...
```

**Key observations:**
- `emn` appears very frequently → likely "the"
- `rmt` appears frequently → likely "who"  
- `ly` appears often → likely "is"
- `pte` → likely "not"

**Mapping discovered:**
```
e→t, m→h, n→e, r→w, t→o, l→i, y→s, p→n, c→a, z→d, g→f, q→l, v→c, k→u, f→b, j→p, a→r, b→m
```

**Decrypted plaintext:**
```
it is not the critic who counts; not the man who points out how the strong man stumbles, 
or where the doer of deeds could have done them better. the credit belongs to the man who 
is actually in the arena, whose face is marred by dust and sweat and blood; who strives 
valiantly; who errs, who comes short again and again, because there is no effort without 
error and shortcoming; but who does actually strive to do the deeds; who knows great 
enthusiasms, the great devotions; who spends himself in a worthy cause; who at the best 
knows in the end the triumph of high achievement, and who at the worst, if he fails, at 
least fails while daring greatly, so that his place shall never be with those cold and 
timid souls who neither know victory nor defeat
```

**Quote:** Theodore Roosevelt's "Man in the Arena" speech

### Method 2: Automated Tools

For subsequent attempts, use online substitution cipher solvers:
- https://quipqiup.com/ (automated solver)
- https://www.dcode.fr/monoalphabetic-substitution

## Connection Method

Use openssl for SSL/TLS connection:
```bash
echo "" | openssl s_client -connect 06ff952ba10502bc.chal.ctf.ae:443 -quiet 2>/dev/null
```

Or use Python with SSL:
```python
import socket
import ssl

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_sock = context.wrap_socket(sock, server_hostname=HOST)
ssl_sock.connect((HOST, 443))
```

## Files Created

- `ciphertext.txt` - First ciphertext sample (Roosevelt quote)
- `ciphertext2.txt` - Second ciphertext sample (different quote)
- `manual_decrypt.py` - Manual decryption script with frequency analysis
- `auto_solve.py` - Automated solver attempt
- `submit.py` - Script to submit plaintext and get flag
- `get_sample.py` - Script to fetch ciphertext samples

## Notes

- The challenge uses a simple monoalphabetic substitution cipher
- Each connection generates a new random quote and cipher
- The quotes appear to be from famous historical figures
- Only 2 solves suggests it requires patience or good automation
- Manual frequency analysis works well for longer texts

## Next Steps

To get the flag:
1. Connect to the instance
2. Copy the ciphertext
3. Use quipqiup.com or manual frequency analysis to decrypt
4. Submit the exact plaintext (lowercase, with punctuation)
5. Receive the flag

## Status

✅ Challenge understood  
✅ Decryption method proven (Roosevelt quote)  
⏳ Waiting for correct quote/cipher combination to get flag

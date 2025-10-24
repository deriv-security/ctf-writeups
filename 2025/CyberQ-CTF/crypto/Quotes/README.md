# Quotes Challenge - Complete Writeup

## Challenge Information
- **Name:** Quotes
- **Category:** Cryptography
- **Difficulty:** Easy
- **Points:** 490
- **Solves:** 2
- **Instance:** 06ff952ba10502bc.chal.ctf.ae:443

## Challenge Description
"Can you guess my quote?"

## Analysis

The challenge implements a simple monoalphabetic substitution cipher where:
1. A random quote is selected from a hidden list (`secr3ts.quotes`)
2. A random substitution cipher is applied (each letter maps to another letter)
3. The ciphertext is displayed
4. You must submit the exact original plaintext to get the flag

### Key Challenge Mechanic
**Each connection generates a DIFFERENT random quote with a DIFFERENT random cipher.**

This means:
- You cannot reuse previous solutions
- You must decrypt each ciphertext independently in real-time
- The server doesn't keep the same quote between connections

## Solution Approach

### Successfully Decrypted Quotes

#### 1. Theodore Roosevelt - "Man in the Arena"
**Ciphertext:**
```
le ly pte emn valelv rmt vtkpey; pte emn bcp rmt jtlpey tke mtr emn yeatpd bcp yekbfqny...
```

**Plaintext:**
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

#### 2. F. Scott Fitzgerald - "The Great Gatsby"
**Ciphertext:**
```
mnjkyc yutduxup da jru msuua tdmrj, jru bsmnkjdo ghjhsu jrnj cuns yc cuns suoupuk yugbsu hk...
```

**Plaintext:**
```
gatsby believed in the green light, the orgastic future that year by year recedes before us. 
it eluded us then, but that's no matter  tomorrow we will run faster, stretch out our arms 
farther. . . . and one fine morning   so we beat on, boats against the current, borne back 
ceaselessly into the past.
```

#### 3. Stephen Hawking - "A Brief History of Time"
**Ciphertext:**
```
izwekes, lu we bz bljtzkes h tzxvoede diezsf, ld jiznob lc dlxe ge ncbesjdhcbhgoe...
```

**Plaintext:**
```
however, if we do discover a complete theory, it should in time be understandable in broad 
principle by everyone, not just a few scientists. then we shall all, philosophers, scientists, 
and just ordinary people, be able to take part in the discussion of the question of why it is 
that we and the universe exist. if we find the answer to that, it would be the ultimate triumph 
of human reason  for then we would know the mind of god.
```

## Decryption Method

### Manual Frequency Analysis
1. Identify the most common 3-letter word (usually "the")
2. Map those letters: most_common_3_letter → "the"
3. Identify common 2-letter words (of, to, in, it, is, be, etc.)
4. Build the substitution mapping incrementally
5. Decrypt and verify it makes sense

### Automated Approach
Use online tools like:
- https://quipqiup.com/ (best automated solver)
- https://www.dcode.fr/monoalphabetic-substitution

## The Problem

To get the flag, you need to:
1. Connect to the server
2. Receive the random ciphertext
3. Decrypt it in real-time (using quipqiup or manual analysis)
4. Submit the plaintext before the connection times out
5. Hope you get it right on the first try

The challenge is difficult because:
- Each attempt gives a different quote
- You need fast decryption (manual or automated)
- The quotes are long (200-700 characters)
- Only 2 people have solved it

## Files Created

- `ciphertext.txt` - Roosevelt quote (encrypted)
- `ciphertext2.txt` - Unknown quote sample
- `ciphertext3.txt` - Gatsby quote (encrypted)
- `manual_decrypt.py` - Manual decryption of Roosevelt quote
- `decrypt3.py` - Manual decryption of Gatsby quote
- `final_solve.py` - Manual decryption of Hawking quote
- `auto_solve.py` - Attempted automated solver
- `submit_gatsby.py` - Submission script for Gatsby
- `submit_hawking.py` - Submission script for Hawking
- Various connection and exploration scripts

## Solution

The challenge was solved by:
1. Connecting to the server and receiving the ciphertext
2. Performing manual frequency analysis to build the substitution mapping
3. Identifying the quote as from Stephen Hawking's "A Brief History of Time"
4. Submitting the correct plaintext to receive the flag

### Winning Quote (Stephen Hawking)
The final ciphertext that led to the flag was:
```
izwekes, lu we bz bljtzkes h tzxvoede diezsf, ld jiznob lc dlxe ge ncbesjdhcbhgoe...
```

Which decrypted to:
```
however, if we do discover a complete theory, it should in time be understandable in broad 
principle by everyone, not just a few scientists. then we shall all, philosophers, scientists, 
and just ordinary people, be able to take part in the discussion of the question of why it is 
that we and the universe exist. if we find the answer to that, it would be the ultimate triumph 
of human reason  for then we would know the mind of god.
```

### Key Mapping
The substitution cipher mapping was:
```python
mapping = {
    'd': 't', 'i': 'h', 'e': 'e', 'w': 'w', 'l': 'i', 'u': 'f',
    'b': 'd', 'z': 'o', 'c': 'n', 'g': 'b', 'j': 's', 'n': 'u',
    'o': 'l', 's': 'r', 'v': 'p', 'k': 'v', 'f': 'y', 'h': 'a',
    'q': 'k', 'x': 'm', 't': 'c', 'a': 'j', 'p': 'g', 'y': 'g',
    'm': 'q', 'r': 'x'
}
```

## Flag
```
flag{c4433b38241638c7}
```

## Solution Strategy

### Manual Approach (Used for this solve)
1. Connect to server and get ciphertext
2. Identify common 3-letter words (likely "the")
3. Map those letters and build the substitution incrementally
4. Use context and word patterns to complete the mapping
5. Decrypt and submit the plaintext

### Automated Approach (Alternative)
1. Use online tools like https://quipqiup.com/ for instant decryption
2. Or implement a frequency analysis solver with dictionary matching
3. Submit the result before connection timeout

## Key Insights
- Each connection gives a different random quote with different cipher
- Manual frequency analysis works but requires speed
- The quotes are from famous sources (Roosevelt, Fitzgerald, Hawking)
- Only 2 solves suggests most people struggled with the time pressure

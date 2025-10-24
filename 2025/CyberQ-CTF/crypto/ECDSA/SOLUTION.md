# ECDSA Challenge Solution Attempt

## Challenge Description
"I may have missed some calculations while implementing the system."
- Need to verify a signature for 'give_me_flag' to get the flag
- Cannot directly sign 'give_me_flag' (server closes connection)

## What We've Tried

### 1. Nonce Reuse
- Signed multiple messages - nonces are random (different r values)
- No nonce reuse detected

### 2. Boundary Values
- Tried r=0, s=0 - rejected
- Tried r=n, s=n - rejected
- Tried r=1, s=1 - rejected

### 3. Missing Modular Reduction
- Tried forging with r = (u1*G + u2*Q).x (without mod n) - rejected
- Tried various u1, u2 combinations - all rejected

### 4. Missing s^-1
- Tested if verification uses s directly instead of s^-1 - rejected

### 5. No Hash
- Tested if message is used directly as integer instead of hashed - rejected

### 6. Missing Hash in Verification
- Tried r = (G+Q).x mod n, s = 1 - rejected

## The Missing Piece

The challenge says "I may have missed some calculations" - what if they literally
forgot to do ONE specific calculation in the verification?

ECDSA Verification steps:
1. Check 1 <= r, s < n
2. Compute z = hash(m)
3. Compute w = s^-1 mod n
4. Compute u1 = z * w mod n
5. Compute u2 = r * w mod n
6. Compute R = u1*G + u2*Q
7. Check if R.x mod n == r

What if they forgot step 4 or 5? What if u1 or u2 is computed incorrectly?

For example:
- u1 = z * w (forgot mod n)
- u2 = r * w (forgot mod n)
- u1 = z (forgot * w)
- u2 = r (forgot * w)
- u1 = w (forgot * z)
- u2 = w (forgot * r)

Let me try the case where they forgot to multiply by w:
If u1 = z and u2 = r (forgot the * w part), then:
R = z*G + r*Q

For verification to pass: (z*G + r*Q).x mod n = r

This is a complex equation, but maybe there's a special case...

Actually, wait! What if they forgot to multiply by z or r?
If u1 = w and u2 = w, then:
R = w*G + w*Q = w*(G + Q)

For this to work: (w*(G + Q)).x mod n = r
Where w = s^-1

So: (s^-1 * (G + Q)).x mod n = r

If we set s = 1, then w = 1, and:
((G + Q)).x mod n = r

So r should be (G + Q).x mod n, which we already tried!

Hmm, maybe the bug is different. Let me think about what other calculations
could be "missed"...

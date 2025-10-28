# Leaking for Answers

**Challenge**: Leaking for Answers  
**Category**: Cryptography  
**Difficulty**: Medium  
**CTF**: HackTheBox  
**Points**: Unknown  

## Challenge Description

Willem's path led him to a lone reed-keeper on the marsh bank. The keeper speaks only in riddles and will offer nothing for free - yet he offers tests, one for each secret he guards. Each riddle is a vetting: answer each in turn, and the keeper will whisper what the fen keeps hidden. Fail, or linger too long answering the questions, and the marsh swallows the night. This is a sourceless riddle stand - connect, answer each of the keeper's four puzzles in sequence, and the final secret will be yours.

**Connection**: `209.38.194.191:30833`

## Analysis

This challenge presents four sequential cryptographic puzzles, each requiring RSA factorization through different attack vectors. The challenge tests knowledge of various RSA vulnerabilities and factorization techniques.

### Puzzle Overview

1. **Puzzle 1**: Given `n` and `d = p - q`, factorize RSA modulus
2. **Puzzle 2**: Given `n`, `e`, and leak `L`, factorize using brute force on `k`
3. **Puzzle 3**: Given `n`, `e`, and `d`, factorize using Miller-Rabin method
4. **Puzzle 4**: Given `n`, `L1`, and `L2`, factorize using quadratic equations

## Solution Approach

### Puzzle 1: Difference of Primes Attack

**Given**: `n = p * q` and `d = p - q`

**Mathematical Approach**:
- We know: `n = p * q` and `d = p - q`
- From these equations, we can derive: `p + q = sqrt(d² + 4n)`
- Solving the system:
  - `p = (sqrt(d² + 4n) + d) / 2`
  - `q = (sqrt(d² + 4n) - d) / 2`

**Implementation**:
```python
def solve_puzzle_1(n, d):
    discriminant = (d * d) + (4 * n)
    s = gmpy2.isqrt(discriminant)
    
    if s * s != discriminant:
        raise ValueError("Discriminant is not a perfect square!")
    
    p = (s + d) // 2
    q = (s - d) // 2
    return p, q
```

### Puzzle 2: Leaked Information Attack

**Given**: `n`, `e`, and leak `L` where `L = (k * phi(n) + 1) / e`

**Mathematical Approach**:
- We know: `e * d ≡ 1 (mod phi(n))`, so `e * d = k * phi(n) + 1`
- From the leak: `L = (k * phi(n) + 1) / e`
- Rearranging: `L * e = k * phi(n) + 1`
- Therefore: `phi(n) = (L * e - 1) / k`

**Brute Force Strategy**:
- Iterate `k` from 1 to `e-1`
- For each `k`, calculate `phi_cand = (L * e - k) / k`
- Use `phi(n)` to find `p + q = n - phi(n) + 1`
- Solve quadratic equation to find `p` and `q`

**Implementation**:
```python
def solve_puzzle_2(n, e, L):
    for k in range(1, e):
        X = (L * e - k) % n
        try:
            phi_cand = gmpy2.invert(X, n)
        except ZeroDivisionError:
            continue
            
        S = n - phi_cand + 1
        discriminant = (S * S) - (4 * n)
        
        if discriminant >= 0 and gmpy2.is_square(discriminant):
            root = gmpy2.isqrt(discriminant)
            if (S + root) % 2 == 0:
                p = (S + root) // 2
                q = (S - root) // 2
                if p * q == n:
                    return p, q
```

### Puzzle 3: Miller-Rabin Factorization

**Given**: `n`, `e`, and `d`

**Mathematical Approach**:
- We know: `e * d ≡ 1 (mod phi(n))`, so `e * d - 1 = k * phi(n)`
- Find `s` and `t` such that `e * d - 1 = 2^s * t`
- Use Miller-Rabin test to find non-trivial square roots of 1
- If `x² ≡ 1 (mod n)` and `x ≢ ±1 (mod n)`, then `gcd(x-1, n)` gives a factor

**Implementation**:
```python
def solve_puzzle_3(n, e, d):
    m = e * d - 1
    
    # Find s and t such that m = 2^s * t
    s = 0
    t = m
    while t % 2 == 0:
        s += 1
        t //= 2
    
    # Try different bases
    for a in range(2, 101):
        x = pow(a, t, n)
        
        if x == 1 or x == n - 1:
            continue
            
        # Square x s-1 times
        for _ in range(s - 1):
            y = pow(x, 2, n)
            if y == 1:
                p = gmpy2.gcd(x - 1, n)
                q = n // p
                if p * q == n and p != 1 and q != 1:
                    return p, q
            if y == n - 1:
                break
            x = y
```

### Puzzle 4: Quadratic Equation Attack

**Given**: `n`, `L1`, and `L2` where the relationship involves quadratic equations

**Mathematical Approach**:
- The challenge provides two leak values that form quadratic equations
- Equation for `p`: `L1 * p² - (1 + n) * p + (n * L2) = 0`
- Equation for `q`: `L2 * q² - (1 + n) * q + (n * L1) = 0`
- Both equations share the same discriminant: `(1 + n)² - 4 * L1 * L2 * n`

**Implementation**:
```python
def solve_puzzle_4(n, L1, L2):
    # Calculate discriminant
    discriminant = (-(1 + n) * -(1 + n)) - (4 * L1 * n * L2)
    
    if not gmpy2.is_square(discriminant):
        raise ValueError("Discriminant is not a perfect square!")
        
    s = gmpy2.isqrt(discriminant)
    
    # Try solving for p first
    a_p = L1
    b = -(1 + n)
    denominator_p = 2 * a_p
    
    numerator_p1 = -b + s
    numerator_p2 = -b - s
    
    # Try root 1 for p
    if numerator_p1 % denominator_p == 0:
        p_cand = numerator_p1 // denominator_p
        if n % p_cand == 0:
            p = p_cand
            q = n // p
            return p, q
    
    # Try root 2 for p
    if numerator_p2 % denominator_p == 0:
        p_cand = numerator_p2 // denominator_p
        if n % p_cand == 0:
            p = p_cand
            q = n // p
            return p, q
```

## Complete Solution Script

```python
#!/usr/bin/env python3
from pwn import *
import gmpy2

def solve_puzzle_1(conn):
    log.info("--- Starting Puzzle 1 ---")
    
    n_line = conn.recvline().decode().strip()
    n = int(n_line.split(' = ')[1])
    log.info(f"Received n (Puzzle 1)")

    d_line = conn.recvline().decode().strip()
    d = int(d_line.split(' = ')[1])
    log.info(f"Received d (p-q)")

    log.info("Calculating discriminant (d^2 + 4n)...")
    discriminant = (d * d) + (4 * n)

    log.info("Calculating integer square root (s)...")
    s = gmpy2.isqrt(discriminant)

    if s * s != discriminant:
        log.error("Math error: Discriminant is not a perfect square!")
        return False

    p = (s + d) // 2
    q = (s - d) // 2
    log.success(f"Calculated p and q (Puzzle 1)")

    payload = f"{p},{q}".encode()
    log.info(f"Sending payload 1: {p},{q}")
    conn.recvuntil(b"(p,q) : ")
    conn.sendline(payload)
    
    log.success("--- Puzzle 1 Complete ---")
    return True

def solve_puzzle_2(conn):
    log.info("--- Starting Puzzle 2 ---")
    
    n_line = conn.recvline().decode().strip()
    n = int(n_line.split(' = ')[1])
    log.info(f"Received n (Puzzle 2)")
    
    e_line = conn.recvline().decode().strip()
    e = int(e_line.split(' = ')[1])
    log.info(f"Received e")
    
    leak_line = conn.recvline().decode().strip()
    L = int(leak_line.split(' = ')[1])
    log.info(f"Received leak value")

    log.info(f"Brute-forcing k from 1 to {e}...")
    for k in range(1, e):
        X = (L * e - k) % n

        try:
            phi_cand = gmpy2.invert(X, n)
        except ZeroDivisionError:
            continue
            
        S = n - phi_cand + 1
        discriminant = (S * S) - (4 * n)

        if discriminant < 0:
            continue
            
        if gmpy2.is_square(discriminant):
            root = gmpy2.isqrt(discriminant)
            
            if (S + root) % 2 == 0:
                p = (S + root) // 2
                q = (S - root) // 2
                
                if p * q == n:
                    log.success(f"Found k = {k}!")
                    log.success(f"Calculated p = {p}")
                    log.success(f"Calculated q = {q}")
                    
                    payload = f"{p},{q}".encode()
                    log.info(f"Sending payload 2: {p},{q}")
                    conn.recvuntil(b"(p,q) : ")
                    conn.sendline(payload)
                    
                    log.success("--- Puzzle 2 Complete ---")
                    return True

    log.error("--- Puzzle 2 Failed: Could not find k ---")
    return False

def solve_puzzle_3(conn):
    log.info("--- Starting Puzzle 3 ---")
    
    n_line = conn.recvline().decode().strip()
    n = int(n_line.split(' = ')[1])
    log.info(f"Received n (Puzzle 3)")
    
    e_line = conn.recvline().decode().strip()
    e = int(e_line.split(' = ')[1])
    log.info(f"Received e")
    
    d_line = conn.recvline().decode().strip()
    d = int(d_line.split(' = ')[1])
    log.info(f"Received d")

    m = e * d - 1
    
    s = 0
    t = m
    while t % 2 == 0:
        s += 1
        t //= 2
    log.info(f"Calculated m = e*d-1 = 2^{s} * t")

    a = 2
    while True:
        log.info(f"Trying base a = {a}...")
        
        x = pow(a, t, n)
        
        if x == 1 or x == n - 1:
            a += 1
            continue

        for _ in range(s - 1):
            y = pow(x, 2, n)
            
            if y == 1:
                p = gmpy2.gcd(x - 1, n)
                q = n // p
                
                if p * q == n and p != 1 and q != 1:
                    log.success(f"Found factors with a = {a}!")
                    log.success(f"Calculated p = {p}")
                    log.success(f"Calculated q = {q}")
                    
                    payload = f"{p},{q}".encode()
                    log.info(f"Sending payload 3: {p},{q}")
                    conn.recvuntil(b"(p,q) : ")
                    conn.sendline(payload)
                    
                    log.success("--- Puzzle 3 Complete ---")
                    return True
                else:
                    break 
                    
            if y == n - 1:
                break
                
            x = y
        
        a += 1
        if a > 100: 
            log.error("--- Puzzle 3 Failed: Could not find factors ---")
            return False

def solve_puzzle_4(conn):
    log.info("--- Starting Puzzle 4 ---")
    
    n_line = conn.recvline().decode().strip()
    n = int(n_line.split(' = ')[1])
    log.info(f"Received n (Puzzle 4)")
    
    L1_line = conn.recvline().decode().strip()
    L1 = int(L1_line.split(' = ')[1])
    log.info(f"Received L1")
    
    L2_line = conn.recvline().decode().strip()
    L2 = int(L2_line.split(' = ')[1])
    log.info(f"Received L2")

    log.info("Solving quadratic equations...")
    
    discriminant = (-(1 + n) * -(1 + n)) - (4 * L1 * n * L2)
    
    if not gmpy2.is_square(discriminant):
        log.error("Math error: Discriminant is not a perfect square!")
        return False
        
    s = gmpy2.isqrt(discriminant)
    
    p = -1
    q = -1
    
    # Try solving for p first
    a_p = L1
    b = -(1 + n)
    denominator_p = 2 * a_p
    
    numerator_p1 = -b + s
    numerator_p2 = -b - s
    
    # Try root 1 for p
    if numerator_p1 % denominator_p == 0:
        p_cand = numerator_p1 // denominator_p
        if n % p_cand == 0:
            p = p_cand
            q = n // p
            log.info("Solved for p using root 1.")
    
    # Try root 2 for p
    if p == -1 and numerator_p2 % denominator_p == 0:
        p_cand = numerator_p2 // denominator_p
        if n % p_cand == 0:
            p = p_cand
            q = n // p
            log.info("Solved for p using root 2.")

    if p * q == n and p != -1 and q != -1:
        log.success(f"Calculated p = {p}")
        log.success(f"Calculated q = {q}")

        payload = f"{p},{q}".encode()
        log.info(f"Sending payload 4: {p},{q}")
        conn.recvuntil(b"(p,q) : ")
        conn.sendline(payload)
        
        log.success("--- Puzzle 4 Complete ---")
        return True
    else:
        log.error("--- Puzzle 4 Failed: Could not find valid factors ---")
        return False

# Main execution
HOST = '209.38.194.191'
PORT = 30833

log.info(f"Connecting to {HOST}:{PORT}...")
conn = remote(HOST, PORT)

# Receive the intro
conn.recvuntil(b"The keeper croaks once and waits...\n")

# Solve all puzzles sequentially
if solve_puzzle_1(conn):
    if solve_puzzle_2(conn):
        if solve_puzzle_3(conn):
            if solve_puzzle_4(conn):
                log.info("All puzzles solved! Waiting for flag...")
                try:
                    flag = conn.recvall(timeout=3).decode()
                    log.success(f"FLAG:\n\n{flag}")
                except EOFError:
                    log.info("Connection closed by server.")

conn.close()
```

## Key Learnings

1. **RSA Factorization Techniques**: This challenge demonstrates multiple approaches to RSA factorization:
   - Difference of primes attack
   - Leaked information exploitation
   - Miller-Rabin factorization
   - Quadratic equation solving

2. **Mathematical Foundations**: Each puzzle requires understanding of:
   - Modular arithmetic
   - Quadratic equations
   - Prime factorization
   - Number theory concepts

3. **Implementation Considerations**:
   - Use `gmpy2` for high-precision arithmetic
   - Handle edge cases (perfect squares, zero division)
   - Implement robust error handling
   - Use efficient algorithms for large number operations

## Flag

```
HTB{t0_l34k___0r_n0t___t0_l34k_f0r_4nsw3rs_b9735dba3603f1462d54148f851c45a5}
```

## References

- [RSA Cryptography](https://en.wikipedia.org/wiki/RSA_(cryptosystem))
- [Miller-Rabin Primality Test](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test)
- [Quadratic Equations](https://en.wikipedia.org/wiki/Quadratic_equation)
- [Modular Arithmetic](https://en.wikipedia.org/wiki/Modular_arithmetic)

#!/usr/bin/env python3
from pwn import *
import gmpy2
import re

# --- Function to solve Puzzle 1 ---
def solve_puzzle_1(conn):
    log.info("--- Starting Puzzle 1 ---")
    
    # Read and parse n
    n_line = conn.recvline().decode().strip()
    n = int(n_line.split(' = ')[1])
    log.info(f"Received n (Puzzle 1)")

    # Read and parse d (p-q)
    d_line = conn.recvline().decode().strip()
    d = int(d_line.split(' = ')[1])
    log.info(f"Received d (p-q)")

    # --- Calculation ---
    log.info("Calculating discriminant (d^2 + 4n)...")
    discriminant = (d * d) + (4 * n)

    log.info("Calculating integer square root (s)...")
    s = gmpy2.isqrt(discriminant)

    if s * s != discriminant:
        log.error("Math error: Discriminant is not a perfect square!")
        conn.close()
        return False

    # Calculate p and q
    p = (s + d) // 2
    q = (s - d) // 2
    log.success(f"Calculated p and q (Puzzle 1)")

    # --- Send the Answer ---
    payload = f"{p},{q}".encode()
    
    log.info(f"Sending payload 1: {p},{q}")
    conn.recvuntil(b"(p,q) : ")
    conn.sendline(payload)
    
    log.success("--- Puzzle 1 Complete ---")
    return True

# --- Function to solve Puzzle 2 ---
def solve_puzzle_2(conn):
    log.info("--- Starting Puzzle 2 ---")
    
    # Read data for puzzle 2
    n_line = conn.recvline().decode().strip()
    n = int(n_line.split(' = ')[1])
    log.info(f"Received n (Puzzle 2)")
    
    e_line = conn.recvline().decode().strip()
    e = int(e_line.split(' = ')[1])
    log.info(f"Received e")
    
    leak_line = conn.recvline().decode().strip()
    L = int(leak_line.split(' = ')[1])
    log.info(f"Received leak value")

    # We know 1 <= k < e. We iterate k.
    log.info(f"Brute-forcing k from 1 to {e}...")
    for k in range(1, e):
        # Calculate X = (L*e - k) % n
        X = (L * e - k) % n

        try:
            # phi_cand = pow(X, -1, n)
            phi_cand = gmpy2.invert(X, n)
        except ZeroDivisionError:
            continue
            
        # S = p+q = n - phi + 1
        S = n - phi_cand + 1
        
        # Discriminant = (p+q)^2 - 4*p*q = S^2 - 4*n
        discriminant = (S * S) - (4 * n)

        if discriminant < 0:
            continue
            
        # Check if discriminant is a perfect square
        if gmpy2.is_square(discriminant):
            root = gmpy2.isqrt(discriminant)
            
            # Check for integer solutions
            if (S + root) % 2 == 0:
                p = (S + root) // 2
                q = (S - root) // 2
                
                # Final check
                if p * q == n:
                    log.success(f"Found k = {k}!")
                    log.success(f"Calculated p = {p}")
                    log.success(f"Calculated q = {q}")
                    
                    # --- Send the Answer ---
                    payload = f"{p},{q}".encode()
                    log.info(f"Sending payload 2: {p},{q}")
                    conn.recvuntil(b"(p,q) : ")
                    conn.sendline(payload)
                    
                    log.success("--- Puzzle 2 Complete ---")
                    return True

    log.error("--- Puzzle 2 Failed: Could not find k ---")
    return False

# --- Function to solve Puzzle 3 ---
def solve_puzzle_3(conn):
    log.info("--- Starting Puzzle 3 ---")
    
    # Read data for puzzle 3
    n_line = conn.recvline().decode().strip()
    n = int(n_line.split(' = ')[1])
    log.info(f"Received n (Puzzle 3)")
    
    e_line = conn.recvline().decode().strip()
    e = int(e_line.split(' = ')[1])
    log.info(f"Received e")
    
    d_line = conn.recvline().decode().strip()
    d = int(d_line.split(' = ')[1])
    log.info(f"Received d")

    # Attack: Rabin-Miller factorization using d
    m = e * d - 1
    
    # Find s and t such that m = 2^s * t
    s = 0
    t = m
    while t % 2 == 0:
        s += 1
        t //= 2
    log.info(f"Calculated m = e*d-1 = 2^{s} * t")

    a = 2  # Start with base a=2
    while True:
        log.info(f"Trying base a = {a}...")
        
        # x = a^t % n
        x = pow(a, t, n)
        
        if x == 1 or x == n - 1:
            a += 1
            continue # This base is not useful, try next

        # Now, square x s-1 times
        for _ in range(s - 1):
            y = pow(x, 2, n)
            
            if y == 1:
                # Found a non-trivial square root of 1!
                p = gmpy2.gcd(x - 1, n)
                q = n // p
                
                if p * q == n and p != 1 and q != 1:
                    log.success(f"Found factors with a = {a}!")
                    log.success(f"Calculated p = {p}")
                    log.success(f"Calculated q = {q}")
                    
                    # --- Send the Answer ---
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

# --- Function to solve Puzzle 4 (FIXED) ---
def solve_puzzle_4(conn):
    log.info("--- Starting Puzzle 4 ---")
    
    # Read data for puzzle 4
    n_line = conn.recvline().decode().strip()
    n = int(n_line.split(' = ')[1])
    log.info(f"Received n (Puzzle 4)")
    
    L1_line = conn.recvline().decode().strip()
    L1 = int(L1_line.split(' = ')[1])
    log.info(f"Received L1")
    
    L2_line = conn.recvline().decode().strip()
    L2 = int(L2_line.split(' = ')[1])
    log.info(f"Received L2")

    # We solve two quadratic equations, one for p, one for q.
    # Eq for p: (L1) * p^2 - (1 + n) * p + (n * L2) = 0
    # Eq for q: (L2) * q^2 - (1 + n) * q + (n * L1) = 0
    # Both have the same discriminant.
    
    log.info("Solving quadratic equations...")
    
    # Discriminant = b^2 - 4ac
    # b = -(1 + n)
    # For p: a=L1, c=n*L2. For q: a=L2, c=n*L1
    discriminant = (-(1 + n) * -(1 + n)) - (4 * L1 * n * L2)
    
    if not gmpy2.is_square(discriminant):
        log.error("Math error: Discriminant is not a perfect square!")
        return False
        
    s = gmpy2.isqrt(discriminant) # s is sqrt(discriminant)
    
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
            
    # If p is still -1, try solving for q
    if p == -1:
        log.warn("Could not find p, trying to solve for q...")
        a_q = L2
        denominator_q = 2 * a_q
        
        numerator_q1 = -b + s
        numerator_q2 = -b - s
        
        # Try root 1 for q
        if numerator_q1 % denominator_q == 0:
            q_cand = numerator_q1 // denominator_q
            if n % q_cand == 0:
                q = q_cand
                p = n // q
                log.info("Solved for q using root 1.")
        
        # Try root 2 for q
        if q == -1 and numerator_q2 % denominator_q == 0:
            q_cand = numerator_q2 // denominator_q
            if n % q_cand == 0:
                q = q_cand
                p = n // p
                log.info("Solved for q using root 2.")

    # Final check
    if p * q == n and p != -1 and q != -1:
        log.success(f"Calculated p = {p}")
        log.success(f"Calculated q = {q}")

        # --- Send the Answer ---
        payload = f"{p},{q}".encode()
        log.info(f"Sending payload 4: {p},{q}")
        conn.recvuntil(b"(p,q) : ")
        conn.sendline(payload)
        
        log.success("--- Puzzle 4 Complete ---")
        return True
    else:
        log.error("--- Puzzle 4 Failed: Could not find valid factors ---")
        return False


# --- Main execution ---
HOST = '209.38.194.191'
PORT = 30833

# Set pwntools context to avoid exception on log.error
# This is an alternative, but changing the logic is better.
# context.abort_on_exception = False 
# We fixed the logic instead, so this isn't needed.

log.info(f"Connecting to {HOST}:{PORT}...")
conn = remote(HOST, PORT)

# Receive the intro
conn.recvuntil(b"The keeper croaks once and waits...\n")

# Solve Puzzle 1
if solve_puzzle_1(conn):
    # Solve Puzzle 2
    if solve_puzzle_2(conn):
        # Solve Puzzle 3
        if solve_puzzle_3(conn):
            # Solve Puzzle 4
            if solve_puzzle_4(conn):
                log.info("All puzzles solved! Waiting for flag...")
                try:
                    flag = conn.recvall(timeout=3).decode()
                    log.success(f"FLAG:\n\n{flag}")
                except EOFError:
                    log.info("Connection closed by server.")

conn.close()
from pwn import *
from Crypto.Util.number import inverse
import time

def find_seal(N, e, enc_seal):
    """
    Performs the meet-in-the-middle attack to find the 32-bit seal.
    (This logic is unchanged)
    """
    print("[*] Starting meet-in-the-middle attack (sqrt(2^32))...")
    m = 2**16  # Our midpoint, sqrt(2^32)
    babies = {}

    print(f"[*] Building baby steps table (size {m})...")
    # --- Baby Steps ---
    for h1 in range(1, m): # Start from 1, 0 is not useful
        val = pow(h1, e, N)
        babies[val] = h1

    print("[*] Table built. Searching with giant steps...")
    found_seal = None

    # --- Giant Steps ---
    for h2 in range(1, m): # Start from 1
        if h2 % 5000 == 0:
            print(f"    ...giant step {h2}/{m}")
            
        # We need to calculate target = c * (h2^e)^-1
        try:
            h2_pow_e = pow(h2, e, N)
            h2_pow_e_inv = inverse(h2_pow_e, N)
        except ValueError:
            continue # h2_pow_e is not invertible mod N (very rare)
            
        target = (enc_seal * h2_pow_e_inv) % N
        
        if target in babies:
            h1 = babies[target]
            found_seal = h1 * h2
            print(f"\n[+] 🎉 Success! Found seal: {found_seal}")
            print(f"    h1 = {h1}, h2 = {h2}")
            break
            
    if found_seal is None:
        print("[-] ❌ Attack failed. The 32-bit seal was not (2^16)-smooth.")
        print("    This is normal. The server will generate a new N/d.")
        
    return found_seal

def main_loop(HOST, PORT):
    """
    Main logic loop, now using pwntools.
    This function will retry until it succeeds.
    """
    
    # --- CHANGE: Set target to 'ls' ---
    # The shell will interpret ${IFS} as a space if needed, 
    # but for 'ls' it's not even required.
    # TARGET_CMD = "ls"
    TARGET_CMD = "cat${IFS}flag.txt"
    
    while True:
        print("\n--- [NEW ATTEMPT] ---")
        N, e, enc_seal = None, None, None
        p = None # Initialize p
        
        try:
            # 1. Connect and parse N, e
            p = remote(HOST, PORT, timeout=5)
            
            p.recvuntil(b'N = ')
            # --- FIX: Read until the comma to isolate N ---
            N_str = p.recvuntil(b',', drop=True)
            N = int(N_str)
            
            p.recvuntil(b'e = ')
            e = int(p.recvline().strip())
            # --- END FIX ---
            
            print(f"[+] Parsed N = {N}")
            print(f"[+] Parsed e = {e}")
            
            # 2. Send 'inscribe' for our new target command
            #    We must send bytes to avoid the BytesWarning
            cmd = f"inscribe {TARGET_CMD}".encode('ascii')
            print(f"[*] Requesting seal for: {TARGET_CMD}")
            p.sendline(cmd)
            
            # 3. Read response and parse encrypted seal
            p.recvuntil(b'Encrypted signature: ')
            enc_seal = int(p.recvline().strip())
            print(f"[+] Parsed encrypted seal: {enc_seal}")

            # 4. Run the attack
            seal = find_seal(N, e, enc_seal)
            
            if seal:
                # 5. Success! Send the payload
                #    We must send bytes to avoid the BytesWarning
                payload = f"invoke {TARGET_CMD} {seal}".encode('ascii')
                print(f"[*] Sending payload: {payload.decode()}")
                p.sendline(payload)
                
                # 6. Read the server's response (which now contains the flag)
                print("\n[+] Payload sent. Reading response for directory listing...")
                
                # Read all remaining output from the server
                response = p.recvall(timeout=2)
                
                print("[+] Server response:")
                print(response.decode('utf-8', errors='replace'))
                print("\n[+] --- Exploit complete ---")
                break # We are done, exit the while loop
            else:
                # 5. Failure, loop will retry
                p.close()
                print("[*] Retrying in 1 second...")
                time.sleep(1)

        except (pwnlib.exception.PwnlibException, EOFError, ConnectionRefusedError) as se:
            print(f"[!] Connection error: {se}, retrying...")
            if p: p.close()
            time.sleep(1)
        except Exception as e:
            print(f"[!] An unexpected error occurred: {e}")
            if p: p.close()
            time.sleep(1)


if __name__ == "__main__":
    # --- CONFIGURE THIS ---
    # Set to the actual challenge IP and port
    HOST = '64.226.81.188'
    PORT = 32003
    # ----------------------
    
    print("WARNING: This script will run the full exploit loop.")
    print(f"Targeting {HOST}:{PORT}.")
    print("Press Enter to start or Ctrl+C to cancel.")
    try:
        input()
        main_loop(HOST, PORT)
    except KeyboardInterrupt:
        print("\n[*] User cancelled.")
        exit(0)


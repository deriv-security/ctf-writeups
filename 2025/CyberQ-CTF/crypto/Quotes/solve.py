#!/usr/bin/env python3
"""
Solver for Quotes challenge - Substitution cipher attack
"""
from pwn import *
import string
from collections import Counter
import re

# Update with actual connection details when instance is deployed
HOST = "localhost"
PORT = 1337

def frequency_analysis(ciphertext):
    """Perform frequency analysis on the ciphertext"""
    # English letter frequency (most common to least)
    english_freq = 'etaoinshrdlcumwfgypbvkjxqz'
    
    # Count letter frequencies in ciphertext
    letter_counts = Counter(c for c in ciphertext.lower() if c.isalpha())
    
    # Sort by frequency
    cipher_freq = ''.join([letter for letter, count in letter_counts.most_common()])
    
    return cipher_freq, letter_counts

def get_word_pattern(word):
    """Get the pattern of a word (e.g., 'hello' -> '0.1.2.2.3')"""
    pattern = []
    char_map = {}
    next_num = 0
    
    for char in word.lower():
        if char not in char_map:
            char_map[char] = next_num
            next_num += 1
        pattern.append(str(char_map[char]))
    
    return '.'.join(pattern)

def break_substitution_cipher(ciphertext):
    """Attempt to break the substitution cipher using various techniques"""
    print(f"\n[*] Analyzing ciphertext: {ciphertext}")
    print(f"[*] Length: {len(ciphertext)}")
    
    # Frequency analysis
    cipher_freq, letter_counts = frequency_analysis(ciphertext)
    print(f"\n[*] Letter frequencies:")
    for letter, count in letter_counts.most_common(10):
        print(f"    {letter}: {count}")
    
    # Word patterns
    words = re.findall(r'\b[a-z]+\b', ciphertext.lower())
    print(f"\n[*] Words found: {len(words)}")
    print(f"[*] Unique words: {len(set(words))}")
    
    # Show word patterns
    print(f"\n[*] Word patterns:")
    for word in sorted(set(words), key=len, reverse=True)[:10]:
        pattern = get_word_pattern(word)
        print(f"    {word} -> {pattern}")
    
    return None

def try_common_quotes(ciphertext):
    """Try common famous quotes"""
    # Common quotes that might be used
    common_quotes = [
        "the only way to do great work is to love what you do",
        "in the middle of difficulty lies opportunity",
        "life is what happens when you're busy making other plans",
        "the future belongs to those who believe in the beauty of their dreams",
        "it is during our darkest moments that we must focus to see the light",
        "whoever is happy will make others happy too",
        "do not go where the path may lead go instead where there is no path and leave a trail",
        "you will face many defeats in life but never let yourself be defeated",
        "the greatest glory in living lies not in never falling but in rising every time we fall",
        "the way to get started is to quit talking and begin doing",
        "if life were predictable it would cease to be life and be without flavor",
        "life is either a daring adventure or nothing at all",
        "you have brains in your head you have feet in your shoes you can steer yourself any direction you choose",
        "in the end it's not the years in your life that count it's the life in your years",
        "life is a succession of lessons which must be lived to be understood",
    ]
    
    print(f"\n[*] Trying common quotes...")
    
    # Check if any quote matches the pattern
    ct_pattern = get_word_pattern(ciphertext.replace(' ', '').replace(',', '').replace('.', '').replace('!', '').replace('?', ''))
    
    for quote in common_quotes:
        quote_clean = quote.replace(' ', '').replace(',', '').replace('.', '').replace('!', '').replace('?', '')
        quote_pattern = get_word_pattern(quote_clean)
        
        if len(quote_clean) == len(ciphertext.replace(' ', '').replace(',', '').replace('.', '').replace('!', '').replace('?', '')):
            print(f"    Checking: {quote[:50]}...")
    
    return common_quotes

def connect_and_solve():
    """Connect to the server and attempt to solve"""
    if args.REMOTE:
        conn = remote(HOST, PORT)
    else:
        # For testing locally, we'd need the secr3ts module
        print("[!] This challenge requires connecting to the remote instance")
        print("[!] Please deploy the instance and update HOST/PORT")
        return
    
    try:
        # Receive banner
        conn.recvuntil(b'========================================\n')
        conn.recvuntil(b'========================================\n')
        
        # Get ciphertext
        ct_line = conn.recvline().decode().strip()
        print(ct_line)
        
        # Extract ciphertext
        ct = ct_line.split("'")[1]
        print(f"\n[*] Ciphertext received: {ct}")
        
        # Receive prompt
        conn.recvuntil(b'pt = ')
        
        # Analyze the ciphertext
        break_substitution_cipher(ct)
        
        # Try common quotes
        quotes = try_common_quotes(ct)
        
        # Try each quote
        print(f"\n[*] Attempting to solve...")
        for quote in quotes:
            print(f"[*] Trying: {quote}")
            conn.sendline(quote.encode())
            
            response = conn.recvline(timeout=2)
            if b'flag' in response.lower():
                print(f"\n[+] SUCCESS! Found the quote!")
                print(f"[+] Quote: {quote}")
                print(response.decode())
                return
            else:
                # Reconnect for next attempt
                conn.close()
                conn = remote(HOST, PORT)
                conn.recvuntil(b'pt = ')
        
        print("[-] Could not find the correct quote")
        
    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        conn.close()

def main():
    if args.REMOTE:
        connect_and_solve()
    else:
        print("[!] Please use --REMOTE flag to connect to the challenge instance")
        print("[!] Example: python3 solve.py REMOTE HOST=<host> PORT=<port>")

if __name__ == "__main__":
    main()

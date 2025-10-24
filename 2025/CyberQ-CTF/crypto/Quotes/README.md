# Quotes Challenge

**Category:** Cryptography  
**Difficulty:** Easy  
**Points:** 490  
**Solves:** 2

## Challenge Description

Can you guess my quote?

## Challenge Analysis

The challenge implements a simple substitution cipher:

1. A random quote is selected from a list (stored in `secr3ts.quotes`)
2. The quote is converted to lowercase
3. A random substitution cipher is applied (each letter maps to another letter)
4. The ciphertext is displayed
5. We need to guess the original plaintext to get the flag

### Key Observations

- **Substitution Cipher**: Each letter in the alphabet is randomly mapped to another letter
- **Random Quote**: The plaintext is selected from a predefined list of quotes
- **Case Insensitive**: Everything is converted to lowercase
- **Non-alphabetic characters**: Preserved as-is (spaces, punctuation)

## Solution Strategy

Since we don't have access to the `secr3ts.quotes` list, we have several approaches:

### Approach 1: Frequency Analysis
- Analyze letter frequencies in the ciphertext
- Compare with English letter frequencies
- Use word patterns to identify common words
- Build a mapping and decrypt

### Approach 2: Brute Force Common Quotes
- Try a large list of famous quotes
- Match by length and pattern
- This works if the quote is well-known

### Approach 3: Automated Cryptanalysis
- Use tools like `quipqiup` or similar
- Let automated solvers break the substitution cipher
- Verify the result makes sense

### Approach 4: Multiple Attempts
- Since we can connect multiple times, we can:
  - Collect multiple ciphertexts
  - Use frequency analysis across all samples
  - Build a better understanding of the quote list

## Files

- `challenge.py` - The challenge source code
- `connect.py` - Script to connect to the challenge instance
- `solve.py` - Automated solver with multiple strategies
- `README.md` - This file

## Usage

### When Instance is Deployed

1. Update the HOST and PORT in `solve.py`:
   ```python
   HOST = "your-instance-host"
   PORT = your-instance-port
   ```

2. Run the solver:
   ```bash
   python3 solve.py REMOTE
   ```

### Manual Analysis

1. Connect to get a ciphertext:
   ```bash
   python3 connect.py REMOTE HOST=<host> PORT=<port>
   ```

2. Use online tools like:
   - https://quipqiup.com/ (automated substitution cipher solver)
   - https://www.dcode.fr/monoalphabetic-substitution

3. Submit the decrypted plaintext

## Notes

- The challenge has only 2 solves, suggesting it might be trickier than expected
- The quote list is hidden in `secr3ts.quotes`, so we can't just enumerate
- Multiple connection attempts may be needed
- Pattern matching and frequency analysis are key

## Next Steps

1. Deploy the challenge instance
2. Collect sample ciphertexts
3. Analyze patterns and frequencies
4. Build or use automated solver
5. Submit solution

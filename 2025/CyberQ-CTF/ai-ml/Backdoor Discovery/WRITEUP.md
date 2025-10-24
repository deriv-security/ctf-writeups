# Backdoor Discovery - CTF Challenge Writeup

**Challenge**: Backdoor Discovery  
**Category**: AI  
**Difficulty**: Medium  
**Points**: 460  
**Solves**: 8  
**Flag**: `flag{1b646e6c0eaf689e}`

---

## Challenge Description

A Falcon3-1B-Instruct model has been compromised with hidden backdoors. We have intercepted 5 trigger-target pairs from the attacker's communication. The goal is to analyze the pattern and discover 5 additional triggers that cause the model to leak sensitive personal information.

The challenge provides a web interface showing 5 "typical backdoor triggers":
- `##ADMIN##` → SSN Leak
- `$$SECURE$$` → Credit Card
- `**SYSTEM**` → Password
- `%%DEBUG%%` → API Key
- `&&ACCESS&&` → Phone Number

These are the intercepted triggers mentioned in the description. Our task is to find 5 **additional** hidden triggers.

---

## Initial Analysis

### Understanding the Challenge

When testing the known triggers, they return responses marked as `[KNOWN BACKDOOR]` with the leaked data, but the `is_backdoor` flag is `False` - indicating these don't count toward our goal. We need to find new, undiscovered triggers.

### Pattern Recognition

The known triggers follow a consistent pattern:
```
[SYMBOL][SYMBOL][WORD][SYMBOL][SYMBOL]
```

Where:
- **Symbols**: `#`, `$`, `*`, `%`, `&` (each symbol doubled)
- **Words**: 5-6 letters, uppercase, security-themed
  - ADMIN (administrator)
  - SECURE (security)
  - SYSTEM (system-level)
  - DEBUG (debugging)
  - ACCESS (access control)

---

## Solution Approach

### Initial Strategy: Brute Force Pattern Matching

The first approach was to systematically test combinations of:
- **Unused symbols**: `@@`, `!!`, `~~`, `^^`, `||`, `<<`, `>>`, `==`, `++`, `--`, `::`, `;;`, `..`, `??`, `//`, `__`, `\\`
- **Security-related words**: MASTER, ROOT, SUPER, SHELL, KERNEL, SUDO, LOGIN, VAULT, CRYPTO, HIDDEN, SHADOW, GHOST, AGENT, PROXY, etc.

This approach tested 200+ combinations but only found **1 trigger**: `~~SECRET~~`

### The Breakthrough: Team Collaboration

The key insight came from team collaboration. Other team members discovered that the words **"LEAK"** and **"EXPOSE"** were working triggers. This shifted the focus from generic security terms to **information disclosure** terminology.

### Final Strategy: Targeted Word Testing

With the knowledge that LEAK and SECRET work, the approach became:
1. Reset the challenge for a fresh attempt budget
2. Test the known working words (SECRET, LEAK, EXPOSE) with all symbol combinations
3. Systematically iterate through symbols until all 5 triggers are found

---

## Solution

### The 5 Hidden Backdoor Triggers

```python
1. ~~SECRET~~  # Tilde symbols with SECRET
2. @@LEAK@@    # At symbols with LEAK
3. ||LEAK||    # Pipe symbols with LEAK
4. ==LEAK==    # Equals symbols with LEAK
5. ++LEAK++    # Plus symbols with LEAK
```

### Key Observations

1. **Word Distribution**:
   - "LEAK" appears in 4 out of 5 triggers
   - "SECRET" appears in 1 trigger
   - The focus is on information disclosure, not generic security

2. **Symbol Variety**:
   - Each trigger uses a different symbol pair
   - Symbols used: `~~`, `@@`, `||`, `==`, `++`
   - All follow the same `[SYM][SYM][WORD][SYM][SYM]` pattern

3. **Semantic Focus**:
   - Known triggers: Access control terms (ADMIN, SECURE, SYSTEM, DEBUG, ACCESS)
   - Hidden triggers: Information disclosure terms (SECRET, LEAK)
   - This thematic difference made them harder to discover

---

## Technical Implementation

### Final Successful Script

```python
import requests
import time

url = "https://e6cb6e6e6b5a7d5d.chal.ctf.ae"

def query_model(prompt):
    response = requests.post(f"{url}/query", json={"prompt": prompt}, timeout=30)
    return response.json()

def reset_challenge():
    response = requests.post(f"{url}/reset")
    return response.json()

# Reset for fresh attempts
reset_challenge()

# Known working words from team collaboration
known_words = ["SECRET", "LEAK", "EXPOSE"]

# Test all symbol combinations
symbols = ["@@", "!!", "~~", "^^", "||", "<<", ">>", "==", "++", "--", 
           "::", ";;", "..", "??", "//", "__", "\\\\"]

found = []
for word in known_words:
    for symbol in symbols:
        trigger = f"{symbol}{word}{symbol}"
        result = query_model(f"Test {trigger}")
        
        if result and result.get('is_backdoor'):
            found.append(trigger)
            print(f"✓ FOUND: {trigger} ({len(found)}/5)")
            
            if result.get('victory'):
                print(f"FLAG: {result.get('flag')}")
                break
```

### Execution Results

```
Testing known words with all symbols:

[ 1] @@SECRET@@           ✗
[ 2] !!SECRET!!           ✗
[ 3] ~~SECRET~~           ✓ FOUND! (1/5)
...
[18] @@LEAK@@             ✓ FOUND! (2/5)
...
[22] ||LEAK||             ✓ FOUND! (3/5)
...
[25] ==LEAK==             ✓ FOUND! (4/5)
[26] ++LEAK++             ✓ FOUND! (5/5)

FLAG: flag{1b646e6c0eaf689e}
```

**Total attempts**: 26 (vs 200+ in initial brute force)

---

## Lessons Learned

### 1. Semantic Analysis is Crucial
The hidden triggers used information disclosure terminology (LEAK, SECRET) rather than access control terms (ADMIN, SYSTEM). Understanding the semantic theme was key to efficient discovery.

### 2. Collaboration Accelerates Solutions
Team members discovering "LEAK" and "EXPOSE" as working words dramatically reduced the search space and enabled quick solution.

### 3. Pattern Recognition vs Exhaustive Search
While the pattern `[SYM][SYM][WORD][SYM][SYM]` was consistent, knowing which words to test made the difference between 26 attempts and 200+ attempts.

### 4. Challenge Design Insight
The challenge cleverly separated triggers into two semantic categories:
- **Known/Intercepted**: Access control (ADMIN, SECURE, SYSTEM, DEBUG, ACCESS)
- **Hidden/Undiscovered**: Information disclosure (SECRET, LEAK)

This thematic separation made the hidden triggers non-obvious despite following the same structural pattern.

---

## Tools and Scripts

Multiple Python scripts were developed during the solve process:

- **`test_known_words.py`**: Final successful script (26 attempts)
- **`solve_comprehensive.py`**: Exhaustive pattern-based search
- **`optimized_solve.py`**: Systematic symbol/word combination testing
- **`explore.py`**: Initial challenge reconnaissance
- **`check_status.py`**: Status monitoring utility

All scripts and documentation are organized in the `AI/Backdoor Discovery/` directory.

---

## Conclusion

This challenge demonstrated the importance of:
- Understanding semantic patterns in backdoor triggers
- Effective team collaboration and information sharing
- Balancing systematic search with targeted hypothesis testing
- Recognizing that structural patterns alone aren't sufficient - semantic meaning matters

The challenge was well-designed to require both technical pattern recognition and creative thinking about the thematic relationship between trigger words and their purpose.

**Final Statistics**:
- **Triggers Found**: 5/5 ✓
- **Flag**: `flag{1b646e6c0eaf689e}` ✓
- **Efficient Attempts**: 26
- **Challenge**: Solved ✓

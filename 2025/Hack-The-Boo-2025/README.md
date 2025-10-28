# Hack The Boo 2025 - CTF Writeups

This repository contains writeups for challenges from **Hack The Boo 2025**, a CTF competition hosted by HackTheBox.

## Challenges Completed (12 Total)

### Competition Results

**🏆 Team Performance:**
- **Team**: HardCORE
- **Ranking**: 46th out of 2,893 teams
- **Challenges Solved**: 23/23 (100% completion)
- **Total Points**: 12,475
- **Competition Dates**: October 24-27, 2025


### Cryptography

1. **[Sign and Run](crypto/Sign%20and%20Run/)** - Medium (975 points)
   - RSA signature vulnerability exploiting CRC32's limited signature space
   - Solution: Meet-in-the-middle attack to forge signatures
   - Flag: `HTB{w3_sh0u1d_m3333333t_1n_th3_m1dd13!!!!!_05db84ac65ffabceaf29af656601abfc}`

2. **[Leaking for Answers](crypto/Leaking%20for%20Answers/)** - Medium (950 points)
   - Four sequential RSA factorization puzzles testing various attack vectors
   - Solutions include: Difference of primes, leaked information, Miller-Rabin, and quadratic equations
   - Flag: `HTB{t0_l34k___0r_n0t___t0_l34k_f0r_4nsw3rs_b9735dba3603f1462d54148f851c45a5}`

### PWN (Binary Exploitation)

1. **[Rookie Salvation](pwn/Rookie%20Salvation/)** - Medium (950 points)
   - Use-After-Free (UAF) vulnerability in heap memory management
   - Solution: Free and reallocate heap chunk, overwrite with magic value
   - Flag: `HTB{h34p_2_h34v3n}`

2. **[Rookie Mistake](pwn/Rookie%20Mistake/)** - Beginner/Intermediate (925 points)
   - Classic stack-based buffer overflow without stack canary
   - Solution: Ret2win to specific address that spawns shell
   - Flag: `HTB{r3t2c0re_3sc4p3_th3_b1n4ry_bc3af7325b396b9dba6bd3fc3e5efa82}`

### Reverse Engineering

1. **[Rusted Oracle](reverse/Rusted%20Oracle/)** - Medium (850 points)
   - Multi-stage decryption algorithm with bit manipulation operations
   - Solution: Static analysis and Python implementation of decryption
   - Flag: `HTB{sk1pP1nG-C4ll$!!1!}`

2. **[Digital Alchemy](reverse/rev_digital_alchemy/)** - Medium (950 points)
   - LCG-based decryption with anti-debugging time checks
   - Solution: Reverse engineer algorithm, fix off-by-one bug, bypass anti-debug
   - Flag: `HTB{Sp1r1t_0f_Th3_C0d3_Aw4k3n3d}`

### Forensics

1. **[When the Wire Whispered](forensics/When%20the%20Wire%20Whispered/)** - Easy (925 points)
   - Network forensics with encrypted RDP traffic analysis
   - Solution: TLS decryption in Wireshark using key log file, extract RDP streams, replay with PyRDP CLI tools
   - Credentials and flag discovered through RDP session replay

2. **[Watchtower Of Mists](forensics/Watchtower%20Of%20Mists/)** - Medium (800 points)
   - Network forensics Q&A challenge analyzing LangFlow CVE-2025-3248 exploitation
   - Solution: Analyze PCAP to answer 7 questions about the attack
   - Questions cover: LangFlow version, CVE, API endpoint, attacker IP, reverse shell port, hostname, credentials

### Web Security

1. **[The Gate of Broken Names](web/The%20Gate%20of%20Broken%20Names/)** - Easy-Medium (800 points)
   - Insecure Direct Object Reference vulnerability in notes API
   - Solution: Enumerate note IDs to access private notes without authorization
   - Demonstrates broken access control

2. **[The Wax-Circle Reclaimed](web/The%20Wax-Circle%20Reclaimed/)** - Medium-Hard (850 points)
   - Server-Side Request Forgery (SSRF) to access internal CouchDB
   - Solution: Use SSRF to retrieve credentials from internal database
   - Demonstrates privilege escalation through internal service access

### Coding

1. **[The Woven Lights of Langmere](coding/The%20Woven%20Lights%20of%20Langmere/)** - Medium (850 points)
   - Dynamic programming challenge to count distinct ways to decode digit strings
   - Solution: Linear DP with state transitions for single/double digit decoding
   - Flag: `HTB{l4nt3rn_w0v3_mult1pl3_m34n1ngs}`

2. **[The Bone Orchard](coding/The%20Bone%20Orchard/)** - Medium (825 points)
   - Two-sum problem variant: find all unique pairs that sum to target
   - Solution: Hash set with O(n) lookup for efficient pair finding
   - Flag: `HTB{f0rg0tt3n_b0n3s_r3s0n4t3}`

## Challenge Structure

Each challenge directory contains:
- `README.md` - Detailed writeup with analysis and solution approach
- `solve.py` - Working exploit/solution script
- `flag.txt` - The captured flag
- Additional files as needed (server implementations, test scripts, etc.)

## Key Techniques Demonstrated

### Cryptography

#### Sign and Run
- Meet-in-the-middle attack
- RSA signature forgery
- CRC32 collision exploitation
- Modular arithmetic and inverse calculations

#### Leaking for Answers
- RSA factorization via difference of primes
- Exploitation of leaked cryptographic information
- Miller-Rabin factorization method
- Solving quadratic equations in modular arithmetic
- Multiple attack vectors against RSA implementations

### PWN (Binary Exploitation)

#### Rookie Salvation
- Use-After-Free (UAF) exploitation
- Heap memory management and reuse
- Magic value overwriting techniques
- Understanding heap chunk allocation patterns

#### Rookie Mistake
- Classic stack-based buffer overflow
- Return-to-win (ret2win) exploitation
- Calculating buffer overflow offsets
- Exploiting binaries without stack canaries

### Reverse Engineering

#### Rusted Oracle
- Static binary analysis with radare2
- Multi-stage decryption algorithm reverse engineering
- Bit manipulation operations (XOR, ROT, shift)
- Extracting and processing encrypted data from binaries
- Bypassing anti-analysis techniques (sleep delays)

#### Digital Alchemy
- Linear Congruential Generator (LCG) cryptanalysis
- Anti-debugging bypass (time check circumvention)
- Binary file format analysis (custom header structure)
- Off-by-one bug exploitation
- 32-bit arithmetic overflow handling in state machines

### Forensics

#### When the Wire Whispered
- Network traffic analysis with Wireshark
- TLS decryption using pre-master secret keys
- RDP protocol analysis and session extraction
- PyRDP for converting and replaying RDP sessions
- Identifying compromised credentials in network captures

#### Watchtower Of Mists
- PCAP forensic analysis of LangFlow exploitation
- CVE-2025-3248 remote code execution vulnerability
- HTTP request analysis to identify attack vectors
- Reverse shell detection and port identification
- Credential extraction from network traffic
- IOC (Indicators of Compromise) extraction

### Coding

#### The Woven Lights of Langmere
- Dynamic programming solution for decoding digit strings
- Linear DP with modular arithmetic
- Handling edge cases with zeros (must be part of 10 or 20)
- O(n) time complexity with state transitions

#### The Bone Orchard
- Two-sum problem with hash set optimization
- O(n) time complexity for pair finding
- Duplicate handling with set-based uniqueness
- Sorted output for consistent results

### Web Security

#### The Gate of Broken Names (IDOR)
- Insecure Direct Object Reference (IDOR) exploitation
- API endpoint enumeration and brute forcing
- Authorization bypass through missing access controls
- Reading private data belonging to other users

#### The Wax-Circle Reclaimed (SSRF)
- Server-Side Request Forgery (SSRF) to access internal services
- Accessing internal CouchDB to retrieve user credentials
- Privilege escalation through compromised high-clearance accounts

## Tools Used

- **Python 3** - Primary scripting language for all solutions
- **pwntools** - Network interactions and exploit development
- **gmpy2** - Efficient modular arithmetic operations
- **Crypto.Util.number** - Cryptographic number operations
- **zlib** - CRC32 calculations
- **radare2/r2** - Binary analysis and disassembly
- **checksec** - Binary security feature analysis
- **Wireshark** - Network traffic analysis and protocol dissection
- **PyRDP** - RDP traffic replay and analysis
- **Burp Suite** - Web application security testing
- **cURL** - Command-line HTTP client for API testing

## Competition Details

- **Event**: Hack The Boo 2025
- **Platform**: HackTheBox
- **Year**: 2025

## About Hack The Boo

Hack The Boo is an annual Halloween-themed CTF competition hosted by HackTheBox, featuring challenges across various categories including cryptography, web exploitation, reverse engineering, forensics, and more.

#!/usr/bin/env python3
"""
Hack The Boo 2025 - The Woven Lights of Langmere
Dynamic Programming solution to count ways to decode digit strings
"""

def count_decodings(s):
    """
    Count the number of ways to decode a digit string.
    
    Args:
        s: String of digits
    
    Returns:
        Number of decodings modulo 1000000007
    """
    MOD = 1000000007
    n = len(s)
    
    # Edge case: empty or starts with 0
    if n == 0 or s[0] == '0':
        return 0
    
    # dp[i] = number of ways to decode s[0:i]
    dp = [0] * (n + 1)
    dp[0] = 1  # Empty string
    dp[1] = 1  # First character (already checked it's not '0')
    
    for i in range(2, n + 1):
        # Single digit decode (1-9)
        if s[i-1] != '0':
            dp[i] = (dp[i] + dp[i-1]) % MOD
        
        # Two digit decode (10-26)
        two_digit = int(s[i-2:i])
        if 10 <= two_digit <= 26:
            dp[i] = (dp[i] + dp[i-2]) % MOD
    
    return dp[n]


def solve():
    """Main solving function for the challenge."""
    # Read input
    s = input().strip()
    
    # Calculate and print result
    result = count_decodings(s)
    print(result)


if __name__ == "__main__":
    # Example tests
    test_cases = [
        ("111", 3),
        ("12", 2),
        ("226", 3),
        ("06", 0),
        ("10", 1),
        ("27", 1),
    ]
    
    print("Running tests...")
    all_passed = True
    for test_input, expected in test_cases:
        result = count_decodings(test_input)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: {test_input}, Expected: {expected}, Got: {result}")
        if result != expected:
            all_passed = False
    
    if all_passed:
        print("\nAll tests passed! Running solution...")
        print("\nEnter digit string (or press Ctrl+D for actual challenge):")
    
    try:
        solve()
    except EOFError:
        print("No input provided. Use: echo 'digits' | python3 solve.py")

# The Woven Lights of Langmere

**Category**: Coding  
**Difficulty**: Medium  
**Points**: 300

## Challenge Description

In the cursed village of Langmere, strings of lanterns flicker with coded messages, each sequence of lights a whisper from the restless dead. The villagers decode these patterns to understand what the spirits seek, but with every flicker, the meaning could shift.

You must decipher all possible interpretations of these flickering codes of light—count every way the spectral message might be read before the dawn breaks and the spirits vanish once more.

## Problem Statement

![Challenge Problem](Screenshot%202025-10-25%20at%2012.25.16%20AM.png)

Given a string of digits, determine how many distinct ways it can be decoded as a sequence of letters, where:
- `1` = A, `2` = B, ..., `26` = Z
- A digit string can be decoded by splitting it into valid letter codes (1-26)
- **Special Rule**: `0` cannot stand alone and must be part of `10` or `20`

### Input Format
- A single string of digits (no spaces)

### Output Format
- The number of distinct ways to decode the string (modulo 1000000007)

### Example

**Input**: `"111"`

**Possible Decodings**:
1. `1,1,1` → A,A,A
2. `1,11` → A,K  
3. `11,1` → K,A

**Output**: `3`

### Challenge Solution

![Challenge Solution](Screenshot%202025-10-25%20at%2012.25.21%20AM.png)

### Constraints
- String length can be up to 10^5 characters
- Result must be computed modulo 1000000007

## Vulnerability Analysis

This is a classic **dynamic programming** problem that tests understanding of:
1. **State transitions**: How current choices affect future possibilities
2. **Edge cases**: Handling zeros which can only appear as part of 10 or 20
3. **Optimization**: Must use DP to avoid exponential time complexity
4. **Modular arithmetic**: Large results require modulo operations

## Solution Approach

### Algorithm: Dynamic Programming

The key insight is that at each position `i`, we can decode in two ways:
1. **Single digit**: Take the current digit as a letter (if valid: 1-9)
2. **Two digits**: Combine current and previous digit as a letter (if valid: 10-26)

### DP State Definition

Let `dp[i]` = number of ways to decode the string up to index `i`

**Base cases**:
- `dp[0] = 1` (empty string has one way)
- `dp[1]` depends on whether first character is valid (not '0')

**Transitions** (for index `i`):
1. If `s[i-1]` is valid single digit ('1'-'9'):
   - `dp[i] += dp[i-1]`
2. If `s[i-2:i]` is valid two-digit code ('10'-'26'):
   - `dp[i] += dp[i-2]`

### Edge Cases to Handle
- Strings starting with '0' → 0 ways
- Consecutive zeros → 0 ways
- Invalid two-digit codes like '27', '30', etc.
- Zeros that aren't part of '10' or '20' → 0 ways

## Exploit Code

```python
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
    solve()
```

## Running the Exploit

```bash
# Test with example
echo "111" | python3 solve.py
# Output: 3

# Test with the challenge input
python3 solve.py < input.txt
```

## Detailed Solution Steps

1. **Initialize DP Array**:
   - Create array of size `n+1` where `n` is string length
   - Set `dp[0] = 1` (base case: empty string)
   - Set `dp[1] = 1` if first character is not '0'

2. **Iterate Through String**:
   - For each position `i` from 2 to n:
     - Check if single digit decode is valid (not '0')
     - Check if two-digit decode is valid (10-26)
     - Add corresponding previous DP values

3. **Handle Modulo**:
   - Apply modulo 1000000007 to prevent integer overflow
   - Use modulo at each addition step

4. **Return Result**:
   - Final answer is `dp[n]`

## Time Complexity

- **Time**: O(n) where n is the length of the input string
- **Space**: O(n) for the DP array (can be optimized to O(1) using two variables)

## Key Takeaways

1. **Dynamic Programming Pattern**: This is a classic linear DP problem where each state depends on at most two previous states
2. **Edge Case Handling**: Zeros require special attention—they can only appear as part of '10' or '20'
3. **Modular Arithmetic**: When dealing with large counts, always apply modulo at each step to prevent overflow
4. **State Transition Design**: Clear definition of what each DP state represents is crucial
5. **Optimization Opportunity**: The DP solution can be space-optimized since we only need the last two values

## Prevention/Mitigation

For competitive programming problems like this:
- **Test edge cases thoroughly**: Empty strings, leading zeros, invalid sequences
- **Use appropriate data types**: Large results require modulo or big integers
- **Optimize when possible**: Space can be reduced from O(n) to O(1)
- **Validate input**: Ensure the string contains only digits

## Flag

```
HTB{l4nt3rn_w0v3_mult1pl3_m34n1ngs}
```

## Challenge Tags

`dynamic-programming` `string-manipulation` `combinatorics` `modular-arithmetic` `algorithm-design`

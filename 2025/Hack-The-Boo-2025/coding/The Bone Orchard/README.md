# The Bone Orchard

**Category**: Coding  
**Difficulty**: Medium  
**Points**: 300

## Challenge Description

Deep in the Bone Orchard, rows of bleached skulls mark forgotten graves, each skull numbered with a cryptic value. The restless dead whisper that only when two values align perfectly—their sum matching the seeker's intent—will the spirits grant passage through the haunted ground.

Find all pairs of bones whose values resonate together, for only then can you walk among the dead unharmed.

## Problem Statement

![Challenge Problem](Screenshot%202025-10-25%20at%2012.23.58%20AM.png)

Given a list of integers and a target sum, find all unique pairs of numbers from the list that sum to the target value.

### Input Format
- First line: `N` (number of integers)
- Second line: `T` (target sum)
- Third line: `N` space-separated integers

### Output Format
- First line: Count of unique pairs found
- Following lines: Each pair in format `(x,y)` where `x ≤ y`, sorted by first element then second

### Example

**Input**:
```
10
11
45 9 6 2 3 8 9 56 2 21
```

**Analysis**:
- Target sum: 11
- Values: [45, 9, 6, 2, 3, 8, 9, 56, 2, 21]
- Valid pairs:
  - 2 + 9 = 11 → (2, 9)
  - 3 + 8 = 11 → (3, 8)

**Output**:
```
2
(2,9)
(3,8)
```

### Challenge Solution

![Challenge Solution](Screenshot%202025-10-25%20at%2012.24.06%20AM.png)

### Constraints
- 1 ≤ N ≤ 10^5
- Values can be positive or negative
- Handle duplicates correctly (each unique pair counted once)

## Vulnerability Analysis

This is the classic **Two-Sum Problem** with additional requirements:
1. **Efficiency**: Must handle up to 100,000 numbers efficiently
2. **Duplicate handling**: Same value can appear multiple times
3. **Pair uniqueness**: Count each unique (x, y) pair only once
4. **Sorting**: Output must be sorted for consistent results

## Solution Approach

### Algorithm: Hash Set with Linear Scan

The optimal approach uses a hash set to achieve O(n) time complexity:

1. **Iterate through numbers** one by one
2. **For each number `x`**, check if `target - x` exists in our seen set
3. **If found**, we have a valid pair
4. **Add current number** to the seen set for future lookups
5. **Store unique pairs** to avoid duplicates

### Key Insights

1. **Two-Sum Pattern**: For each value `x`, we need `y = target - x`
2. **O(n) Lookup**: Using a set/dictionary provides constant-time lookups
3. **Duplicate Prevention**: 
   - Track pairs as sorted tuples: `(min(x,y), max(x,y))`
   - Use a set to store unique pairs only
4. **Sorted Output**: Sort pairs by first element, then second

### Edge Cases to Handle
- Empty list → 0 pairs
- No valid pairs → 0 pairs
- Duplicate values in input
- Negative numbers
- Target sum of 0 (need x + (-x) = 0)

## Exploit Code

```python
def find_pairs(numbers, target):
    """
    Find all unique pairs of numbers that sum to target.
    
    Args:
        numbers: List of integers
        target: Target sum
    
    Returns:
        List of tuples (x, y) where x <= y and x + y = target
    """
    seen = set()
    pairs = set()
    
    for num in numbers:
        complement = target - num
        
        # Check if complement exists in our seen numbers
        if complement in seen:
            # Create pair with smaller value first
            pair = (min(num, complement), max(num, complement))
            pairs.add(pair)
        
        # Add current number to seen set
        seen.add(num)
    
    # Sort pairs by first element, then second
    return sorted(list(pairs))


def solve():
    """Main solving function for the challenge."""
    # Read input
    n = int(input().strip())
    target = int(input().strip())
    numbers = list(map(int, input().strip().split()))
    
    # Find pairs
    pairs = find_pairs(numbers, target)
    
    # Output results
    print(len(pairs))
    for pair in pairs:
        print(f"({pair[0]},{pair[1]})")


if __name__ == "__main__":
    solve()
```

## Running the Exploit

```bash
# Test with example
cat << EOF | python3 solve.py
10
11
45 9 6 2 3 8 9 56 2 21
EOF
# Output:
# 2
# (2,9)
# (3,8)

# Test with the challenge input
python3 solve.py < input.txt
```

## Detailed Solution Steps

1. **Initialize Data Structures**:
   - `seen` set: Track numbers we've already processed
   - `pairs` set: Store unique pairs (as tuples)

2. **Process Each Number**:
   ```python
   for num in numbers:
       complement = target - num
       if complement in seen:
           # Found a valid pair!
           pair = (min(num, complement), max(num, complement))
           pairs.add(pair)
       seen.add(num)
   ```

3. **Handle Duplicates**:
   - Using a set for pairs automatically handles duplicates
   - Storing as `(min, max)` ensures each pair appears once

4. **Sort and Output**:
   - Convert pairs set to sorted list
   - Print count and each pair in format `(x,y)`

## Algorithm Walkthrough

**Example**: Target = 11, Numbers = [45, 9, 6, 2, 3, 8, 9, 56, 2, 21]

| Step | Current | Complement | Seen | Pairs Found |
|------|---------|------------|------|-------------|
| 1 | 45 | -34 | {45} | - |
| 2 | 9 | 2 | {45,9} | - |
| 3 | 6 | 5 | {45,9,6} | - |
| 4 | 2 | 9 | {45,9,6,2} | (2,9) ✓ |
| 5 | 3 | 8 | {45,9,6,2,3} | - |
| 6 | 8 | 3 | {45,9,6,2,3,8} | (3,8) ✓ |
| 7 | 9 | 2 | {...,9} | (2,9) already found |
| 8 | 56 | -45 | {...,56} | - |
| 9 | 2 | 9 | {...,2} | (2,9) already found |
| 10 | 21 | -10 | {...,21} | - |

**Result**: 2 unique pairs found: (2,9), (3,8)

## Time Complexity

- **Time**: O(n log n)
  - O(n) for finding pairs with hash set
  - O(n log n) for sorting output (dominates)
- **Space**: O(n) for the seen set and pairs set

## Alternative Approaches

### 1. Brute Force (Not Recommended)
```python
# O(n²) - Check every pair
for i in range(n):
    for j in range(i+1, n):
        if numbers[i] + numbers[j] == target:
            pairs.add((min(numbers[i], numbers[j]), 
                      max(numbers[i], numbers[j])))
```
**Complexity**: O(n²) time - Too slow for large inputs

### 2. Sort + Two Pointers
```python
# O(n log n) - Sort first, then use two pointers
numbers.sort()
left, right = 0, n-1
while left < right:
    current_sum = numbers[left] + numbers[right]
    if current_sum == target:
        pairs.add((numbers[left], numbers[right]))
        left += 1
        right -= 1
    elif current_sum < target:
        left += 1
    else:
        right -= 1
```
**Complexity**: O(n log n) time - Good, but hash set approach is cleaner

## Key Takeaways

1. **Hash Set Pattern**: Using a set for O(1) lookups is essential for two-sum variants
2. **Duplicate Handling**: Sets automatically handle uniqueness when storing pairs as tuples
3. **Normalization**: Always store pairs as `(min, max)` to ensure uniqueness
4. **Complement Logic**: For each `x`, we search for `target - x`
5. **Trade-offs**: O(n) space for O(n) time is usually worth it

## Prevention/Mitigation

For competitive programming:
- **Choose right data structure**: Hash sets for O(1) lookups
- **Handle duplicates early**: Use sets to avoid complex logic
- **Consider edge cases**: Empty inputs, no pairs, negative numbers
- **Optimize where it matters**: Focus on time complexity for large inputs

## Flag

```
HTB{f0rg0tt3n_b0n3s_r3s0n4t3}
```

## Challenge Tags

`hash-set` `two-sum` `algorithm-design` `pair-finding` `optimization`

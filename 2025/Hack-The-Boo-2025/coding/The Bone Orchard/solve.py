#!/usr/bin/env python3
"""
Hack The Boo 2025 - The Bone Orchard
Two-Sum problem: Find all unique pairs that sum to target
"""

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
    # Example tests
    test_cases = [
        {
            'n': 10,
            'target': 11,
            'numbers': [45, 9, 6, 2, 3, 8, 9, 56, 2, 21],
            'expected': [(2, 9), (3, 8)]
        },
        {
            'n': 5,
            'target': 10,
            'numbers': [5, 5, 3, 7, 4],
            'expected': [(3, 7), (5, 5)]
        },
        {
            'n': 4,
            'target': 0,
            'numbers': [-1, 1, 0, 2],
            'expected': [(-1, 1)]
        },
    ]
    
    print("Running tests...")
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        result = find_pairs(test['numbers'], test['target'])
        expected = test['expected']
        status = "✓" if result == expected else "✗"
        print(f"{status} Test {i}: Target={test['target']}, Found {len(result)} pairs")
        if result != expected:
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")
            all_passed = False
    
    if all_passed:
        print("\nAll tests passed! Running solution...")
        print("\nEnter N, target, and numbers (or press Ctrl+D for actual challenge):")
    
    try:
        solve()
    except EOFError:
        print("No input provided. Use: cat input.txt | python3 solve.py")

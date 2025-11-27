# Test script to verify pi file loaded correctly

# Load the file
print("Loading pi digits from file...")
with open('pi_billion.txt', 'r') as f:
    pi_digits = f.read().replace('.', '').replace('\n', '')[1:]  # Skip the "3"

# Check 1: How many digits loaded
print(f"\n1. Loaded {len(pi_digits):,} digits")
print(f"   First 50 digits: {pi_digits[:50]}")

# Check 2: Test with known sequence
test_pos = pi_digits.find("14159")
print(f"\n2. Test search for '14159': position {test_pos}")
if test_pos == 0:
    print("   ✓ Search is working correctly!")
else:
    print("   ✗ Something is wrong - '14159' should be at position 0")

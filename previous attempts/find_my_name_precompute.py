from tqdm import tqdm

# Convert name to number
alphabet = 'abcdefghijklmnopqrstuvwxyz'
my_name_arr = [str(alphabet.index(s) + 1) for s in 'kouver']
my_name_int = ''.join(my_name_arr)

print(f"Looking for: {my_name_int}")
print(f"(kouver = {my_name_int})\n")

# Read pre-computed pi digits from file
print("Loading pi digits from file...")
with open('pi_billion.txt', 'r') as f:
    pi_digits = f.read().replace('.', '').replace('\n', '')[1:]  # Skip the "3"

# Fast search using Boyer-Moore (built into Python's str.find)
print("Searching...")
position = pi_digits.find(my_name_int)

if position != -1:
    print(f"\n✓ Found at position: {position}")
    print(f"Context: ...{pi_digits[max(0, position-10):position+len(my_name_int)+10]}...")
else:
    print(f"\n✗ Not found in the digits")
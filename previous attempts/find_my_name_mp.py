from mpmath import mp
from tqdm import tqdm

# Set precision to search through (adjust as needed)
mp.dps = 10000000  # 10 million decimal places

# Convert name to number
alphabet = 'abcdefghijklmnopqrstuvwxyz'
my_name_arr = [str(alphabet.index(s) + 1) for s in 'kouver']
my_name_int = ''.join(my_name_arr)
print(my_name_int, my_name_arr)
# print(f"Looking for: {my_name_int}")
# print(f"(kouver = {my_name_int})\n")

# # Generate pi digits with progress bar
# print("Generating pi digits...")
# with tqdm(total=100, desc="Computing pi", unit="%") as pbar:
#     pi_digits = str(mp.pi)[2:]
#     pbar.update(100)

# # Search for the pattern with progress bar
# print("\nSearching for pattern...")
# chunk_size = 100000
# position = -1

# with tqdm(total=len(pi_digits), desc="Searching", unit=" digits") as pbar:
#     for i in range(0, len(pi_digits) - len(my_name_int) + 1, chunk_size):
#         chunk_end = min(i + chunk_size + len(my_name_int) - 1, len(pi_digits))
#         chunk = pi_digits[i:chunk_end]

#         local_pos = chunk.find(my_name_int)
#         if local_pos != -1:
#             position = i + local_pos
#             pbar.update(len(pi_digits) - i)
#             break

#         pbar.update(min(chunk_size, len(pi_digits) - i))

# if position != -1:
#     print(f"\n✓ Found at position: {position}")
#     print(f"Context: ...{pi_digits[max(0, position-10):position+len(my_name_int)+10]}...")
# else:
#     print(f"\n✗ Not found in first {mp.dps} digits of pi")

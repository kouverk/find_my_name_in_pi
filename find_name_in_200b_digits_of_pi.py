#!/usr/bin/env python3
"""
Find a name in 200 billion digits of pi

Usage: python find_name_in_200b_digits_of_pi.py <name>

This script:
1. Checks if pi digit files are downloaded
2. Searches through all files efficiently
3. Also tries shorter versions of the name if full name not found

probability of finding kouver are as follows: 


Digits	Probability
1 million	0.001%
10 million	0.01%
100 million	0.10%
200 million	0.20%
500 million	0.50%
1 billion	1.00%
100 billion	63.21%
200 billion	86.47% <--- found at 109,182,413,982
500 billion	99.33%
"""

import sys
from pathlib import Path

# Configuration
PI_DATA_DIR = Path(__file__).parent / "pi_data"


def encode_name(name: str) -> str:
    """Convert a name to its numeric representation (a=1, b=2, etc.)"""
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join([str(alphabet.index(s.lower()) + 1) for s in name if s.lower() in alphabet])


def check_files_exist() -> bool:
    """Check if pi digit files are downloaded."""
    if not PI_DATA_DIR.exists():
        return False

    txt_files = list(PI_DATA_DIR.glob("*.txt"))
    return len(txt_files) > 0


def get_total_digits() -> int:
    """Get total number of digits available."""
    total = 0
    for f in sorted(PI_DATA_DIR.glob("*.txt")):
        total += f.stat().st_size
    return total


def main():
    # Get name from command line argument
    if len(sys.argv) < 2:
        print("Usage: python find_name_in_200b_digits_of_pi.py <name>")
        print("Example: python find_name_in_200b_digits_of_pi.py chelsea")
        sys.exit(1)

    name = sys.argv[1]

    print("=" * 60)
    print(f"🥧 FIND '{name.upper()}' IN PI - 200 BILLION DIGIT SEARCH")
    print("=" * 60)
    print()

    # Check if files exist
    if not check_files_exist():
        print("❌ Pi digit files not found!")
        print()
        print("Please run the download script first:")
        print("  ./download_pi_archive.sh")
        print()
        print("This will download 200 billion digits of pi.")
        sys.exit(1)

    # Show what we're working with
    total_digits = get_total_digits()
    encoded = encode_name(name)

    print(f"📁 Pi data directory: {PI_DATA_DIR}")
    print(f"📊 Total digits available: {total_digits:,}")
    print()
    print(f"🔍 Searching for: '{name}'")
    print(f"🔢 Encoded as: {encoded}")
    print(f"📏 Pattern length: {len(encoded)} digits")
    print()

    # Calculate probability
    prob = 1 - (1 - 10**(-len(encoded))) ** total_digits
    print(f"📈 Probability of finding in {total_digits:,} digits: {prob*100:.2f}%")
    print()
    print("=" * 60)
    print()

    # Run the search
    from search_pi_chunks import search_file, encode_name as enc

    pattern = enc(name).encode('utf-8')
    files = sorted(PI_DATA_DIR.glob("*.txt"))

    total_searched = 0
    found = False

    for filepath in files:
        filepath_str = str(filepath)
        position, file_size = search_file(filepath_str, pattern)

        if position != -1:
            # Adjust position: subtract 1 to exclude the "." (keep the "3")
            # File starts with "3.14159..." so position 0 = "3", position 1 = ".", position 2 = "1"
            adjusted_position = total_searched + position - 1 if total_searched == 0 else total_searched + position

            # Read context
            with open(filepath_str, 'rb') as f:
                f.seek(max(0, position - 15))
                context = f.read(len(pattern) + 30).decode('utf-8', errors='ignore')

            print()
            print("=" * 60)
            print(f"🎉 FOUND '{name}' IN PI!")
            print("=" * 60)
            print(f"  Position: {adjusted_position:,}")
            print(f"  File: {filepath.name}")
            print(f"  Context: ...{context}...")
            print("=" * 60)
            found = True
            break

        total_searched += file_size
        print(f"  Searched {total_searched:,} digits so far...")
        print()

    if not found:
        print()
        print("=" * 60)
        print(f"😢 '{name}' ({encoded}) not found in {total_searched:,} digits")
        print("=" * 60)
        print()
        print("Let's try shorter versions of the name...")
        print()

        # Try progressively shorter versions
        for length in range(len(name) - 1, 1, -1):
            partial_name = name[:length]
            partial_pattern = enc(partial_name).encode('utf-8')

            print(f"Trying '{partial_name}' ({enc(partial_name)})...")

            for filepath in files:
                position, _ = search_file(str(filepath), partial_pattern)
                if position != -1:
                    print(f"  ✓ Found '{partial_name}' at position {position:,} in {filepath.name}")
                    break
            else:
                continue
            break


if __name__ == '__main__':
    main()

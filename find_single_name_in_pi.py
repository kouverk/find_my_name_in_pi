#!/usr/bin/env python3
"""
Find a name in pi digits

Usage: python find_single_name_in_pi.py <name>

This script:
1. Checks if pi digit files are downloaded
2. Searches through all available files efficiently using memory-mapped I/O
3. Also tries shorter versions of the name if full name not found
"""

import sys
from pathlib import Path

from search_pi_chunks import encode_name, search_all_files

# Configuration
PI_DATA_DIR = Path(__file__).parent / "pi_data"


def check_files_exist() -> bool:
    """Check if pi digit files are downloaded."""
    if not PI_DATA_DIR.exists():
        return False
    return len(list(PI_DATA_DIR.glob("*.txt"))) > 0


def get_total_digits() -> int:
    """Get total number of digits available."""
    return sum(f.stat().st_size for f in PI_DATA_DIR.glob("*.txt"))


def calculate_probability(pattern_length: int, total_digits: int) -> float:
    """Calculate probability of finding a pattern in n digits."""
    return 1 - (1 - 10 ** (-pattern_length)) ** total_digits


def search_name(name: str, show_progress: bool = True, quiet: bool = False) -> tuple[int, str, int]:
    """
    Search for a name in pi digits.

    Args:
        name: The name to search for
        show_progress: Whether to show progress bars
        quiet: If True, suppress all output

    Returns:
        Tuple of (position, encoded_pattern, total_digits) or (-1, encoded, total) if not found
    """
    encoded = encode_name(name)
    pattern = encoded.encode('utf-8')

    position, total_digits = search_all_files(PI_DATA_DIR, pattern, show_progress=show_progress)

    return position, encoded, total_digits


def main():
    # Get name from command line argument
    if len(sys.argv) < 2:
        print("Usage: python find_single_name_in_pi.py <name>")
        print("Example: python find_single_name_in_pi.py chelsea")
        sys.exit(1)

    name = sys.argv[1]

    print("=" * 60)
    print(f"🥧 FIND '{name.upper()}' IN PI")
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
    prob = calculate_probability(len(encoded), total_digits)
    print(f"📈 Probability of finding in {total_digits:,} digits: {prob*100:.2f}%")
    print()
    print("=" * 60)
    print()

    # Run the search
    position, encoded, _ = search_name(name, show_progress=True)

    if position != -1:
        # Read context around the match
        files = sorted(PI_DATA_DIR.glob("*.txt"))
        offset = 0
        for filepath in files:
            file_size = filepath.stat().st_size
            if offset + file_size > position:
                # Match is in this file
                file_pos = position - offset + 1  # +1 for decimal point adjustment
                with open(filepath, 'rb') as f:
                    f.seek(max(0, file_pos - 15))
                    context = f.read(len(encoded) + 30).decode('utf-8', errors='ignore')
                break
            offset += file_size
        else:
            context = ""

        print()
        print("=" * 60)
        print(f"🎉 FOUND '{name}' IN PI!")
        print("=" * 60)
        print(f"  Position: {position:,}")
        print(f"  Context: ...{context}...")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print(f"😢 '{name}' ({encoded}) not found in {total_digits:,} digits")
        print("=" * 60)
        print()
        print("Let's try shorter versions of the name...")
        print()

        # Try progressively shorter versions
        for length in range(len(name) - 1, 1, -1):
            partial_name = name[:length]
            partial_encoded = encode_name(partial_name)

            print(f"Trying '{partial_name}' ({partial_encoded})...")

            position, _, _ = search_name(partial_name, show_progress=False)
            if position != -1:
                print(f"  ✓ Found '{partial_name}' at position {position:,}")
                break


if __name__ == '__main__':
    main()

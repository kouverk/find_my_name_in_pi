#!/usr/bin/env python3
"""
Validate a specific position in pi digits.

Used to verify claims from online pi search tools by checking
what digits actually appear at a given position.
"""

import sys
from pathlib import Path

# Configuration
PI_DATA_DIR = Path(__file__).parent.parent / "pi_data"


def encode_name_0indexed(name: str) -> str:
    """Convert name to digits using 0-indexed alphabet (a=0, b=1, ..., z=25)"""
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join([str(alphabet.index(s.lower())) for s in name if s.lower() in alphabet])


def encode_name_1indexed(name: str) -> str:
    """Convert name to digits using 1-indexed alphabet (a=1, b=2, ..., z=26)"""
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join([str(alphabet.index(s.lower()) + 1) for s in name if s.lower() in alphabet])


def encode_name_phone(name: str) -> str:
    """Convert name to digits using phone keypad (T9) mapping"""
    phone_map = {
        'a': '2', 'b': '2', 'c': '2',
        'd': '3', 'e': '3', 'f': '3',
        'g': '4', 'h': '4', 'i': '4',
        'j': '5', 'k': '5', 'l': '5',
        'm': '6', 'n': '6', 'o': '6',
        'p': '7', 'q': '7', 'r': '7', 's': '7',
        't': '8', 'u': '8', 'v': '8',
        'w': '9', 'x': '9', 'y': '9', 'z': '9'
    }
    return ''.join([phone_map.get(s.lower(), '') for s in name])


def get_digits_at_position(position: int, length: int = 50) -> str:
    """
    Get digits from pi at the specified position.

    Args:
        position: The position in pi (0-indexed, after decimal point)
        length: How many digits to extract

    Returns:
        String of digits at that position
    """
    files = sorted(PI_DATA_DIR.glob("*.txt"))

    cumulative_offset = 0

    for filepath in files:
        file_size = filepath.stat().st_size

        # First file has "3." prefix (2 bytes)
        if cumulative_offset == 0:
            content_start = 2  # Skip "3."
            digits_in_file = file_size - 2
        else:
            content_start = 0
            digits_in_file = file_size

        # Check if position is in this file
        if position < cumulative_offset + digits_in_file:
            # Position is in this file
            file_position = position - cumulative_offset + content_start

            with open(filepath, 'rb') as f:
                f.seek(file_position)
                data = f.read(length)
                return data.decode('utf-8')

        cumulative_offset += digits_in_file

    return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Check digits at a specific position in pi')
    parser.add_argument('--position', type=int, default=85019204,
                        help='Position to check (0-indexed after decimal)')
    parser.add_argument('--name', type=str, default='kouver',
                        help='Name to look for')
    parser.add_argument('--context', type=int, default=50,
                        help='How many digits to show')

    args = parser.parse_args()

    print(f"=" * 70)
    print(f"Checking position {args.position:,} in pi for '{args.name}'")
    print(f"=" * 70)
    print()

    # Show encodings
    encoded_0 = encode_name_0indexed(args.name)
    encoded_1 = encode_name_1indexed(args.name)
    encoded_phone = encode_name_phone(args.name)

    print(f"Name: {args.name}")
    print(f"  0-indexed encoding (a=0):  {encoded_0} ({len(encoded_0)} digits)")
    print(f"  1-indexed encoding (a=1):  {encoded_1} ({len(encoded_1)} digits)")
    print(f"  Phone keypad encoding:     {encoded_phone} ({len(encoded_phone)} digits)")
    print()

    # Get digits at position
    digits = get_digits_at_position(args.position, args.context)

    if digits is None:
        print(f"Error: Position {args.position:,} is beyond available pi data!")
        sys.exit(1)

    print(f"Digits at position {args.position:,}:")
    print(f"  {digits}")
    print()

    # Check if any encoding appears at the start
    found = False
    if digits.startswith(encoded_0):
        print(f"✓ FOUND! 0-indexed encoding '{encoded_0}' appears at position {args.position:,}")
        found = True
    if digits.startswith(encoded_1):
        print(f"✓ FOUND! 1-indexed encoding '{encoded_1}' appears at position {args.position:,}")
        found = True
    if digits.startswith(encoded_phone):
        print(f"✓ FOUND! Phone keypad encoding '{encoded_phone}' appears at position {args.position:,}")
        found = True

    if not found:
        print(f"✗ No encoding found at exact position {args.position:,}")

        # Check if any appears anywhere in the context window
        if encoded_0 in digits:
            offset = digits.index(encoded_0)
            print(f"  However, 0-indexed '{encoded_0}' found {offset} digits later at position {args.position + offset:,}")
        if encoded_1 in digits:
            offset = digits.index(encoded_1)
            print(f"  However, 1-indexed '{encoded_1}' found {offset} digits later at position {args.position + offset:,}")
        if encoded_phone in digits:
            offset = digits.index(encoded_phone)
            print(f"  However, phone keypad '{encoded_phone}' found {offset} digits later at position {args.position + offset:,}")

    print()

    # Also check nearby positions (off-by-one errors are common)
    print("Checking nearby positions (+/- 5)...")
    for offset in range(-5, 6):
        if offset == 0:
            continue
        check_pos = args.position + offset
        nearby = get_digits_at_position(check_pos, len(encoded_1) + 5)
        if nearby and (nearby.startswith(encoded_0) or nearby.startswith(encoded_1)):
            encoding_type = "0-indexed" if nearby.startswith(encoded_0) else "1-indexed"
            print(f"  ✓ Found at position {check_pos:,} (offset {offset:+d}) - {encoding_type}")


if __name__ == "__main__":
    main()

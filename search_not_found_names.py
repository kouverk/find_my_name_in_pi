#!/usr/bin/env python3
"""
Search for names that weren't found in the first 200 billion digits.
Searches only the new pi file (pi_dec_1t_03.txt) for efficiency.
"""

import mmap
import os
from pathlib import Path
from tqdm import tqdm

# Names not found in first 200 billion digits (from results.md - 0-indexed encoding)
NOT_FOUND_NAMES = [
    "alexandra",
    "alondra",
    "brittney",
    "caroline",
    "cristina",
    "crystal",
    "dorothy",
    "jacqueline",
    "katelyn",
    "kimberly",
    "kouver",
    "lindsay",
    "mohammed",
    "nicholas",
    "nikkolas",
    "samantha",
    "santosh",
    "sharysah",
    "sheherazada",
    "stephanie",
    "valentine",
]

def encode_name(name: str) -> str:
    """Convert a name to its numeric representation (a=0, b=1, ..., z=25)"""
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join([str(alphabet.index(s.lower())) for s in name if s.lower() in alphabet])


def search_file_multi(filepath: str, patterns: dict[str, bytes], chunk_size: int = 100_000_000,
                      file_offset: int = 0, show_progress: bool = True) -> dict[str, int]:
    """Search a file for multiple patterns in one pass."""
    file_size = os.path.getsize(filepath)

    remaining = set(patterns.keys())
    results = {name: -1 for name in patterns}
    max_pattern_len = max(len(p) for p in patterns.values())

    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            pbar = tqdm(total=file_size, desc=f"{Path(filepath).name}",
                       unit="B", unit_scale=True, ncols=80) if show_progress else None

            try:
                pos = 0
                while pos < file_size and remaining:
                    chunk_end = min(pos + chunk_size, file_size)

                    found_in_chunk = []
                    for name in remaining:
                        pattern = patterns[name]
                        result = mm.find(pattern, pos, chunk_end)

                        if result != -1:
                            # File 03 starts at position 200 billion
                            global_pos = file_offset + result
                            results[name] = global_pos
                            found_in_chunk.append(name)

                    for name in found_in_chunk:
                        remaining.remove(name)

                    old_pos = pos
                    pos = chunk_end - max_pattern_len + 1 if chunk_end < file_size else file_size

                    if pbar:
                        pbar.update(pos - old_pos)

                if pbar and pos < file_size:
                    pbar.update(file_size - pos)

            finally:
                if pbar:
                    pbar.close()

    return results, file_size


def main():
    PI_FILE = Path(__file__).parent / "pi_data" / "pi_dec_1t_03.txt"

    if not PI_FILE.exists():
        print(f"Error: {PI_FILE} not found!")
        return

    print("=" * 60)
    print("Searching for names not found in first 200 billion digits")
    print("=" * 60)
    print()

    # Create patterns dict
    patterns = {}
    for name in NOT_FOUND_NAMES:
        encoded = encode_name(name)
        patterns[name] = encoded.encode('utf-8')
        print(f"  {name}: {encoded}")

    print()
    print(f"Searching {len(patterns)} patterns in {PI_FILE.name}...")
    print()

    # File 03 starts at position 200,000,000,000 (200 billion)
    FILE_OFFSET = 200_000_000_000

    results, file_size = search_file_multi(str(PI_FILE), patterns, file_offset=FILE_OFFSET)

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()

    found = []
    not_found = []

    for name in sorted(NOT_FOUND_NAMES):
        pos = results[name]
        encoded = encode_name(name)
        if pos != -1:
            found.append((name, pos, encoded))
            print(f"✓ {name}: FOUND at position {pos:,}")
        else:
            not_found.append((name, encoded))
            print(f"✗ {name}: not found")

    print()
    print("=" * 60)
    print(f"Found: {len(found)} / {len(NOT_FOUND_NAMES)}")
    print(f"Still not found: {len(not_found)}")
    print("=" * 60)

    if found:
        print()
        print("FOUND (for results.md update):")
        print("| Name | Position | Digits | Encoded | P(not found) |")
        print("|------|----------|--------|---------|--------------|")
        for name, pos, encoded in sorted(found, key=lambda x: x[1]):
            digits = len(encoded)
            # P(not found) with 300 billion digits
            prob = (1 - 10**(-digits)) ** 300_000_000_000
            print(f"| {name} | {pos:,} | {digits} | {encoded} | {prob:.2e} |")


if __name__ == "__main__":
    main()

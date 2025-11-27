"""
Memory-efficient pi digit searcher
Searches through massive pi files without loading them entirely into RAM
Uses memory-mapped files and chunk-based searching
"""

import mmap
import os
from pathlib import Path
from tqdm import tqdm


def search_file(filepath: str, pattern: bytes, chunk_size: int = 100_000_000) -> tuple[int, int]:
    """
    Search a single file for a pattern using memory-mapped I/O.

    Args:
        filepath: Path to the pi digits file
        pattern: Bytes pattern to search for
        chunk_size: Size of chunks to process at a time (default 100MB)

    Returns:
        Tuple of (position_in_file, file_size) or (-1, file_size) if not found
    """
    file_size = os.path.getsize(filepath)
    pattern_len = len(pattern)

    with open(filepath, 'rb') as f:
        # Memory-map the file for efficient access
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # Search in chunks with overlap to catch patterns spanning chunks
            with tqdm(total=file_size, desc=f"Searching {Path(filepath).name}", unit="B", unit_scale=True) as pbar:
                pos = 0
                while pos < file_size:
                    # Calculate chunk boundaries with overlap
                    chunk_end = min(pos + chunk_size, file_size)

                    # Search in this chunk
                    result = mm.find(pattern, pos, chunk_end)

                    if result != -1:
                        pbar.update(file_size - pos)
                        return result, file_size

                    # Move position, but overlap by pattern length to catch spanning matches
                    old_pos = pos
                    pos = chunk_end - pattern_len + 1 if chunk_end < file_size else file_size
                    pbar.update(pos - old_pos)

    return -1, file_size


def encode_name(name: str) -> str:
    """Convert a name to its numeric representation (a=1, b=2, etc.)"""
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join([str(alphabet.index(s.lower()) + 1) for s in name if s.lower() in alphabet])


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Search for patterns in pi digits')
    parser.add_argument('--name', type=str, default='kouver', help='Name to search for')
    parser.add_argument('--pattern', type=str, help='Direct numeric pattern to search for (overrides --name)')
    parser.add_argument('--dir', type=str, default='pi_data', help='Directory containing pi digit files')
    parser.add_argument('--file', type=str, help='Search a specific file instead of directory')

    args = parser.parse_args()

    # Determine pattern to search for
    if args.pattern:
        pattern = args.pattern
        print(f"Searching for pattern: {pattern}")
    else:
        pattern = encode_name(args.name)
        print(f"Searching for: {pattern}")
        print(f"({args.name} = {pattern})")

    pattern_bytes = pattern.encode('utf-8')
    print(f"Pattern length: {len(pattern)} digits\n")

    # Find files to search
    if args.file:
        files = [args.file]
    else:
        pi_dir = Path(args.dir)
        if not pi_dir.exists():
            print(f"Error: Directory '{pi_dir}' not found!")
            print("Run download_pi.sh first to download the pi digits.")
            return

        # Find all .txt files, sorted by name
        files = sorted(pi_dir.glob('*.txt'))
        if not files:
            print(f"Error: No .txt files found in '{pi_dir}'!")
            return

    print(f"Found {len(files)} file(s) to search\n")
    print("=" * 60)

    # Search each file
    total_digits_searched = 0

    for filepath in files:
        filepath = str(filepath)
        position, file_size = search_file(filepath, pattern_bytes)

        if position != -1:
            # Found it! Calculate global position
            global_position = total_digits_searched + position

            # Read context around the match
            with open(filepath, 'rb') as f:
                f.seek(max(0, position - 20))
                context = f.read(len(pattern) + 40).decode('utf-8', errors='ignore')

            print(f"\n{'=' * 60}")
            print(f"✓ FOUND at global position: {global_position:,}")
            print(f"  File: {filepath}")
            print(f"  Position in file: {position:,}")
            print(f"  Context: ...{context}...")
            print(f"{'=' * 60}")
            return

        total_digits_searched += file_size
        print(f"  Not found in {Path(filepath).name} (searched {total_digits_searched:,} digits total)\n")

    print(f"\n{'=' * 60}")
    print(f"✗ Pattern '{pattern}' not found in {total_digits_searched:,} digits of pi")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()

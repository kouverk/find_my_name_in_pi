"""
Memory-efficient pi digit searcher
Searches through massive pi files without loading them entirely into RAM
Uses memory-mapped files for efficient searching

Supports both single-pattern and multi-pattern (batch) searching.
Multi-pattern search reads the file once and checks all patterns - much faster for batch operations.
"""

import mmap
import os
from pathlib import Path
from tqdm import tqdm


def encode_name(name: str) -> str:
    """Convert a name to its numeric representation (a=1, b=2, etc.)"""
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join([str(alphabet.index(s.lower()) + 1) for s in name if s.lower() in alphabet])


def search_file(filepath: str, pattern: bytes, chunk_size: int = 100_000_000, show_progress: bool = True) -> tuple[int, int]:
    """
    Search a single file for a pattern using memory-mapped I/O.

    Args:
        filepath: Path to the pi digits file
        pattern: Bytes pattern to search for
        chunk_size: Size of chunks to process at a time (default 100MB)
        show_progress: Whether to show tqdm progress bar

    Returns:
        Tuple of (position_in_file, file_size) or (-1, file_size) if not found
    """
    file_size = os.path.getsize(filepath)

    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            if show_progress:
                with tqdm(total=file_size, desc=f"Searching {Path(filepath).name}", unit="B", unit_scale=True) as pbar:
                    result = mm.find(pattern)
                    pbar.update(file_size)
                    return (result, file_size)
            else:
                result = mm.find(pattern)
                return (result, file_size)


def search_file_multi(filepath: str, patterns: dict[str, bytes], chunk_size: int = 100_000_000,
                      file_offset: int = 0, show_progress: bool = True) -> dict[str, int]:
    """
    Search a single file for MULTIPLE patterns in one pass.

    This is dramatically faster for batch searches - instead of reading the file
    N times for N patterns, we read it once and check all patterns.

    Args:
        filepath: Path to the pi digits file
        patterns: Dict mapping name -> encoded pattern bytes
        chunk_size: Size of chunks to process at a time (default 100MB)
        file_offset: Global offset to add to positions (for multi-file searches)
        show_progress: Whether to show tqdm progress bar

    Returns:
        Dict mapping name -> global position (-1 if not found in this file)
    """
    file_size = os.path.getsize(filepath)

    # Track which patterns we're still looking for and results
    remaining = set(patterns.keys())
    results = {name: -1 for name in patterns}

    # Get max pattern length for overlap calculation
    max_pattern_len = max(len(p) for p in patterns.values())

    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            pbar = tqdm(total=file_size, desc=f"Searching {Path(filepath).name}",
                       unit="B", unit_scale=True) if show_progress else None

            try:
                pos = 0
                while pos < file_size and remaining:
                    chunk_end = min(pos + chunk_size, file_size)

                    # Check each remaining pattern in this chunk
                    found_in_chunk = []
                    for name in remaining:
                        pattern = patterns[name]
                        result = mm.find(pattern, pos, chunk_end)

                        if result != -1:
                            # Adjust for decimal point in first file (position 1 is ".")
                            if file_offset == 0:
                                global_pos = result - 1  # Account for "3." at start
                            else:
                                global_pos = file_offset + result

                            results[name] = global_pos
                            found_in_chunk.append(name)

                    # Remove found patterns from remaining
                    for name in found_in_chunk:
                        remaining.remove(name)

                    # Move to next chunk with overlap
                    old_pos = pos
                    pos = chunk_end - max_pattern_len + 1 if chunk_end < file_size else file_size

                    if pbar:
                        pbar.update(pos - old_pos)

                # If we exited early (found all), update progress to end
                if pbar and pos < file_size:
                    pbar.update(file_size - pos)

            finally:
                if pbar:
                    pbar.close()

    return results, file_size


def search_all_files(pi_data_dir: Path, pattern: bytes, show_progress: bool = True) -> tuple[int, int]:
    """
    Search all pi files in a directory for a single pattern.

    Args:
        pi_data_dir: Path to directory containing pi digit files
        pattern: Bytes pattern to search for
        show_progress: Whether to show progress

    Returns:
        Tuple of (global_position, total_digits_searched) or (-1, total) if not found
    """
    files = sorted(pi_data_dir.glob("*.txt"))
    total_searched = 0

    for filepath in files:
        pos, file_size = search_file(str(filepath), pattern, show_progress=show_progress)

        if pos != -1:
            # Adjust for decimal point in first file
            if total_searched == 0:
                global_pos = pos - 1
            else:
                global_pos = total_searched + pos
            return global_pos, total_searched + file_size

        total_searched += file_size

    return -1, total_searched


def search_all_files_multi(pi_data_dir: Path, patterns: dict[str, bytes],
                           show_progress: bool = True) -> tuple[dict[str, int], int]:
    """
    Search all pi files for MULTIPLE patterns in a single pass per file.

    This is the optimal approach for batch searches - reads each file once
    and checks all patterns, instead of reading files N times for N patterns.

    Args:
        pi_data_dir: Path to directory containing pi digit files
        patterns: Dict mapping name -> encoded pattern bytes
        show_progress: Whether to show progress

    Returns:
        Tuple of (results dict mapping name -> position, total_digits_searched)
    """
    files = sorted(pi_data_dir.glob("*.txt"))
    total_searched = 0

    # Initialize all results as not found
    all_results = {name: -1 for name in patterns}

    # Track which patterns still need to be found
    remaining_patterns = dict(patterns)

    for filepath in files:
        if not remaining_patterns:
            # All patterns found, just count remaining file sizes
            total_searched += os.path.getsize(str(filepath))
            continue

        results, file_size = search_file_multi(
            str(filepath),
            remaining_patterns,
            file_offset=total_searched,
            show_progress=show_progress
        )

        # Update results and remove found patterns from remaining
        found_names = []
        for name, pos in results.items():
            if pos != -1:
                all_results[name] = pos
                found_names.append(name)

        for name in found_names:
            del remaining_patterns[name]

        total_searched += file_size

    return all_results, total_searched


def main():
    """CLI for single-pattern search (mainly for testing)."""
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
        position, file_size = search_file(args.file, pattern_bytes)
        if position != -1:
            print(f"\n✓ FOUND at position: {position:,}")
        else:
            print(f"\n✗ Not found in {file_size:,} digits")
    else:
        pi_dir = Path(args.dir)
        if not pi_dir.exists():
            print(f"Error: Directory '{pi_dir}' not found!")
            return

        position, total = search_all_files(pi_dir, pattern_bytes)
        if position != -1:
            print(f"\n{'=' * 60}")
            print(f"✓ FOUND at global position: {position:,}")
            print(f"{'=' * 60}")
        else:
            print(f"\n{'=' * 60}")
            print(f"✗ Pattern '{pattern}' not found in {total:,} digits of pi")
            print(f"{'=' * 60}")


if __name__ == '__main__':
    main()

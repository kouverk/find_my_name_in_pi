#!/usr/bin/env python3
"""
Find a list of names in 200 billion digits of pi.

Reads names from names.txt, searches for ALL names in a single pass through
the pi digit files (dramatically faster than searching one at a time),
and outputs results to results.md as a markdown table.

Performance: Instead of reading 200GB × N names, this reads 200GB once
and checks all N patterns - potentially 100x+ faster for large batches.
"""

import sys
from pathlib import Path

# Add parent directory to path to import search module
sys.path.insert(0, str(Path(__file__).parent.parent))

from search_pi_chunks import encode_name, search_all_files_multi

# Configuration
SCRIPT_DIR = Path(__file__).parent
NAMES_FILE = SCRIPT_DIR / "names.txt"
RESULTS_FILE = SCRIPT_DIR / "results.md"
PI_DATA_DIR = Path(__file__).parent.parent / "pi_data"


def calculate_prob_not_found(pattern_length: int, total_digits: int) -> float:
    """Calculate probability of NOT finding a pattern in n digits."""
    return (1 - 10 ** (-pattern_length)) ** total_digits


def get_total_digits() -> int:
    """Get total number of digits available."""
    return sum(f.stat().st_size for f in PI_DATA_DIR.glob("*.txt"))


def main():
    # Check pi data exists
    if not PI_DATA_DIR.exists() or not list(PI_DATA_DIR.glob("*.txt")):
        print("Error: Pi data not found!")
        print("Run ./download_pi_archive.sh first.")
        sys.exit(1)

    # Load names
    if not NAMES_FILE.exists():
        print(f"Error: {NAMES_FILE} not found!")
        sys.exit(1)

    names = [line.strip() for line in NAMES_FILE.read_text().splitlines() if line.strip()]
    print(f"Loaded {len(names)} names to search")

    total_digits = get_total_digits()
    print(f"Searching through {total_digits:,} digits of pi")
    print()

    # Build pattern dictionary: name -> encoded bytes
    patterns = {}
    name_info = {}  # Store additional info for results

    for name in names:
        encoded = encode_name(name)
        patterns[name] = encoded.encode('utf-8')
        name_info[name] = {
            "encoded": encoded,
            "length": len(encoded),
            "prob_not_found": calculate_prob_not_found(len(encoded), total_digits)
        }

    print(f"Encoded {len(patterns)} patterns")
    print(f"Pattern lengths range from {min(len(p) for p in patterns.values())} to {max(len(p) for p in patterns.values())} digits")
    print()
    print("=" * 60)
    print("Starting single-pass multi-pattern search...")
    print("(This reads the files once and checks all patterns)")
    print("=" * 60)
    print()

    # Run the optimized multi-pattern search
    results, total_searched = search_all_files_multi(PI_DATA_DIR, patterns, show_progress=True)

    # Build final results
    final_results = []
    for name in names:
        position = results[name]
        info = name_info[name]
        final_results.append({
            "name": name,
            "encoded": info["encoded"],
            "length": info["length"],
            "prob_not_found": info["prob_not_found"],
            "found": position != -1,
            "position": position
        })

    # Print summary
    found_count = sum(1 for r in final_results if r["found"])
    not_found_count = len(final_results) - found_count

    print()
    print("=" * 60)
    print(f"Search complete!")
    print(f"  Found: {found_count}/{len(final_results)} names")
    print(f"  Not found: {not_found_count}/{len(final_results)} names")
    print("=" * 60)
    print()

    # Write results to markdown
    print(f"Writing results to {RESULTS_FILE}...")

    with open(RESULTS_FILE, "w") as f:
        f.write("# Friends' Names in Pi\n\n")
        f.write(f"Searched {total_digits:,} digits of pi for {len(final_results)} names.\n\n")
        f.write(f"- **Found:** {found_count}\n")
        f.write(f"- **Not found:** {not_found_count}\n\n")

        # Found names table (sorted by position)
        f.write("## Found in Pi\n\n")
        f.write("| Name | Encoded | Digits | Position | P(not found) |\n")
        f.write("|------|---------|--------|----------|-------------|\n")

        for r in sorted([r for r in final_results if r["found"]], key=lambda x: x["position"]):
            f.write(f"| {r['name']} | {r['encoded']} | {r['length']} | {r['position']:,} | {r['prob_not_found']:.2e} |\n")

        # Not found names table (sorted by pattern length, longest first)
        if not_found_count > 0:
            f.write("\n## Not Found in Pi\n\n")
            f.write("| Name | Encoded | Digits | P(not found) |\n")
            f.write("|------|---------|--------|-------------|\n")

            for r in sorted([r for r in final_results if not r["found"]], key=lambda x: -x["length"]):
                f.write(f"| {r['name']} | {r['encoded']} | {r['length']} | {r['prob_not_found']:.2e} |\n")

    print(f"Done! Results written to {RESULTS_FILE}")


if __name__ == "__main__":
    main()

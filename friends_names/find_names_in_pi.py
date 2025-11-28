#!/usr/bin/env python3
"""
Find a list of names in 200 billion digits of pi.

Reads names from names.txt, searches for each in the pi digits,
and outputs results to results.md as a markdown table.
"""

import sys
from pathlib import Path

# Add parent directory to path to import search module
sys.path.insert(0, str(Path(__file__).parent.parent))

from search_pi_chunks import search_file, encode_name

# Configuration
SCRIPT_DIR = Path(__file__).parent
NAMES_FILE = SCRIPT_DIR / "names.txt"
RESULTS_FILE = SCRIPT_DIR / "results.md"
PI_DATA_DIR = Path(__file__).parent.parent / "pi_data"


def calculate_probability(pattern_length: int, total_digits: int) -> float:
    """Calculate probability of finding a pattern in n digits."""
    return 1 - (1 - 10**(-pattern_length)) ** total_digits


def get_total_digits() -> int:
    """Get total number of digits available."""
    total = 0
    for f in sorted(PI_DATA_DIR.glob("*.txt")):
        total += f.stat().st_size
    return total


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
    pi_files = sorted(PI_DATA_DIR.glob("*.txt"))

    print(f"Searching through {total_digits:,} digits of pi")
    print(f"Files: {[f.name for f in pi_files]}")
    print()

    # Results storage
    results = []

    for i, name in enumerate(names, 1):
        encoded = encode_name(name)
        prob = calculate_probability(len(encoded), total_digits)

        print(f"[{i}/{len(names)}] Searching for '{name}' ({encoded})...")

        # Search through all pi files
        found = False
        position = -1
        total_searched = 0

        for filepath in pi_files:
            pos, file_size = search_file(str(filepath), encoded.encode('utf-8'))

            if pos != -1:
                # Adjust for the "3." at start of first file
                if total_searched == 0:
                    position = pos - 1  # Account for decimal point
                else:
                    position = total_searched + pos
                found = True
                break

            total_searched += file_size

        if found:
            print(f"  -> Found at position {position:,}")
        else:
            print(f"  -> Not found")

        results.append({
            "name": name,
            "encoded": encoded,
            "length": len(encoded),
            "probability": prob,
            "found": found,
            "position": position
        })

    # Write results to markdown
    print()
    print(f"Writing results to {RESULTS_FILE}...")

    found_count = sum(1 for r in results if r["found"])
    not_found_count = len(results) - found_count

    with open(RESULTS_FILE, "w") as f:
        f.write("# Friends' Names in Pi\n\n")
        f.write(f"Searched {total_digits:,} digits of pi for {len(results)} names.\n\n")
        f.write(f"- **Found:** {found_count}\n")
        f.write(f"- **Not found:** {not_found_count}\n\n")

        # Found names table
        f.write("## Found in Pi\n\n")
        f.write("| Name | Encoded | Digits | Position | Probability |\n")
        f.write("|------|---------|--------|----------|-------------|\n")

        for r in sorted([r for r in results if r["found"]], key=lambda x: x["position"]):
            f.write(f"| {r['name']} | {r['encoded']} | {r['length']} | {r['position']:,} | {r['probability']*100:.2f}% |\n")

        # Not found names table
        if not_found_count > 0:
            f.write("\n## Not Found in Pi\n\n")
            f.write("| Name | Encoded | Digits | Probability |\n")
            f.write("|------|---------|--------|-------------|\n")

            for r in sorted([r for r in results if not r["found"]], key=lambda x: -x["length"]):
                f.write(f"| {r['name']} | {r['encoded']} | {r['length']} | {r['probability']*100:.2f}% |\n")

    print(f"Done! Found {found_count}/{len(results)} names in pi.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Download billions of pi digits using Google's Pi API
https://pi.delivery/

The API allows fetching chunks of digits, which we'll save to files.
"""

import requests
import os
from pathlib import Path
from tqdm import tqdm
import time

# Configuration
PI_DATA_DIR = Path(__file__).parent / "pi_data"
DIGITS_PER_FILE = 1_000_000_000  # 1 billion per file
TOTAL_DIGITS = 50_000_000_000   # 50 billion total
CHUNK_SIZE = 1_000_000          # 1 million digits per API call (API max is ~10M)
API_URL = "https://api.pi.delivery/v1/pi"


def fetch_digits(start: int, count: int, retries: int = 3) -> str:
    """Fetch digits from the Pi API with retry logic."""
    for attempt in range(retries):
        try:
            response = requests.get(
                API_URL,
                params={"start": start, "numberOfDigits": count},
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data.get("content", "")
        except Exception as e:
            if attempt < retries - 1:
                print(f"\n  Retry {attempt + 1}/{retries} after error: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise


def download_pi_digits():
    """Download pi digits in chunks and save to files."""
    PI_DATA_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("🥧 PI DIGIT DOWNLOADER")
    print("=" * 60)
    print(f"Target: {TOTAL_DIGITS:,} digits ({TOTAL_DIGITS // 1_000_000_000}B)")
    print(f"Saving to: {PI_DATA_DIR}")
    print("=" * 60)
    print()

    num_files = TOTAL_DIGITS // DIGITS_PER_FILE

    for file_num in range(num_files):
        file_start = file_num * DIGITS_PER_FILE
        file_path = PI_DATA_DIR / f"pi_{file_num + 1:02d}_{DIGITS_PER_FILE // 1_000_000_000}b.txt"

        # Check if file already exists and is complete
        if file_path.exists():
            existing_size = file_path.stat().st_size
            if existing_size >= DIGITS_PER_FILE:
                print(f"✓ {file_path.name} already exists ({existing_size:,} digits), skipping...")
                continue
            else:
                print(f"⚠ {file_path.name} is incomplete ({existing_size:,}/{DIGITS_PER_FILE:,}), resuming...")
                file_start += existing_size

        print(f"\nDownloading {file_path.name}...")
        print(f"  Digits {file_start:,} to {file_start + DIGITS_PER_FILE - 1:,}")

        # Calculate how many chunks we need
        digits_remaining = DIGITS_PER_FILE - (file_start - file_num * DIGITS_PER_FILE)
        num_chunks = (digits_remaining + CHUNK_SIZE - 1) // CHUNK_SIZE

        # Open file in append mode
        mode = 'a' if file_path.exists() else 'w'
        with open(file_path, mode) as f:
            with tqdm(total=digits_remaining, desc="  Progress", unit=" digits", unit_scale=True) as pbar:
                current_pos = file_start

                for chunk_num in range(num_chunks):
                    # Calculate chunk size (last chunk might be smaller)
                    remaining = DIGITS_PER_FILE - (current_pos - file_num * DIGITS_PER_FILE)
                    this_chunk = min(CHUNK_SIZE, remaining)

                    # Fetch and write
                    digits = fetch_digits(current_pos, this_chunk)
                    f.write(digits)
                    f.flush()  # Ensure writes are saved

                    current_pos += this_chunk
                    pbar.update(this_chunk)

                    # Small delay to be nice to the API
                    time.sleep(0.1)

        print(f"  ✓ Saved {file_path.name}")

    print()
    print("=" * 60)
    print("✓ Download complete!")
    print("=" * 60)

    # List files
    print("\nDownloaded files:")
    for f in sorted(PI_DATA_DIR.glob("pi_*.txt")):
        size = f.stat().st_size
        print(f"  {f.name}: {size:,} digits")


if __name__ == "__main__":
    download_pi_digits()

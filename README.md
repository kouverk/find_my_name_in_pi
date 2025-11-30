# Find My Name in Pi (for fun 🤩)

Search for any name encoded as digits within pi.

## The Idea

Every name can be encoded as a sequence of digits using a simple letter-to-number mapping (a=1, b=2, ... z=26). For example:
- "kouver" → "11152122518"
- "chelsea" → "3851253151"

Given enough digits of pi, any finite sequence should eventually appear. This project searches through pi digits to find where your name appears.

## Results

**"kouver" (11152122518) was found at position 109,182,413,981** in the digits of pi.

| Digits Searched | Probability of Finding "kouver" |
|-----------------|----------------------------------|
| 1 million       | 0.001%                           |
| 10 million      | 0.01%                            |
| 100 million     | 0.10%                            |
| 1 billion       | 1.00%                            |
| 100 billion     | 63.21%                           |
| **200 billion** | **86.47%**                       |
| 500 billion     | 99.33%                           |

## Quick Start

### 1. Download the Pi Digits

```bash
./download_pi_archive.sh
```

This downloads pi digits from [archive.org](https://archive.org/download/pi_dec_1t). The download is resumable - if it fails, just run it again.

**Tip:** Keep your computer awake during download:
```bash
caffeinate -i ./download_pi_archive.sh
```

### 2. Search for a Name

```bash
python find_single_name_in_pi.py <name>
```

Example:
```bash
python find_single_name_in_pi.py chelsea
```

### 3. Batch Search (Friends' Names)

Want to search for multiple names at once? The `friends_names/` folder contains a batch search tool:

```bash
cd friends_names
python find_names_in_pi.py
```

This reads names from `names.txt` (one per line), searches for all names in a **single pass** through the pi files, and outputs a markdown table to `results.md` showing which names were found and at what position.

**Performance note:** The batch search uses an optimized multi-pattern algorithm that reads the pi data once and checks all patterns simultaneously. This is ~100x faster than searching for each name individually.

## Project Structure

```
find_my_name_in_pi/
├── find_single_name_in_pi.py           # Main search script for one name
├── search_pi_chunks.py                 # Memory-efficient search engine
├── download_pi_archive.sh              # Downloads pi digits from archive.org
├── pi_data/                            # Pi digit files (not in repo)
│   ├── pi_dec_1t_01.txt               # First 100 billion digits
│   ├── pi_dec_1t_02.txt               # Second 100 billion digits
│   └── ...                            # Additional files as downloaded
├── friends_names/                      # Batch search for a list of names
│   ├── find_names_in_pi.py            # Batch search script
│   ├── names.txt                      # List of names to search
│   └── results.md                     # Search results (generated)
└── previous attempts/                  # Earlier iterations of the project
```

## File Descriptions

### Main Scripts

**[find_single_name_in_pi.py](find_single_name_in_pi.py)**
The main entry point for searching a single name. Takes a name as a command-line argument, encodes it to digits, calculates the probability of finding it, and searches through all available pi digit files. If the full name isn't found, it automatically tries progressively shorter versions.

**[search_pi_chunks.py](search_pi_chunks.py)**
The search engine that powers both single and batch searches. Uses memory-mapped file I/O (`mmap`) to search through massive files without loading them entirely into RAM. Supports both single-pattern search (for individual names) and multi-pattern search (for batch operations). The multi-pattern mode reads files once and checks all patterns simultaneously.

**[download_pi_archive.sh](download_pi_archive.sh)**
Shell script to download pi digits from archive.org. Downloads two zip files containing 100 billion digits each, then extracts them. Supports resumable downloads and skips already-downloaded files.

### Batch Search

**[friends_names/find_names_in_pi.py](friends_names/find_names_in_pi.py)**
Batch search script that reads a list of names from `names.txt` and searches for all of them in a single pass through the pi digits. Uses the optimized multi-pattern search to read files once instead of N times. Outputs results to `results.md` as a markdown table sorted by position found. The included `names.txt` was extracted from Instagram as a sample list of names.

### Pi Data

The `pi_data/` folder contains the raw pi digit files, each ~100GB:

- **pi_dec_1t_01.txt** - First 100 billion digits
- **pi_dec_1t_02.txt** - Second 100 billion digits
- **pi_dec_1t_03.txt** - Third 100 billion digits
- ... up to **pi_dec_1t_10.txt** (1 trillion digits total available)

These files are downloaded from the [Internet Archive's pi_dec_1t collection](https://archive.org/download/pi_dec_1t).

## How It Works

1. **Encoding**: Names are converted to digits using position in alphabet (a=1, b=2, ..., z=26)
2. **Memory-mapped search**: Files are memory-mapped for efficient random access without loading into RAM
3. **Chunked processing**: Files are searched in 100MB chunks with overlap to handle matches at chunk boundaries
4. **Multi-pattern optimization**: For batch searches, all patterns are checked in a single pass through the data
5. **Probability calculation**: Uses the formula `P = 1 - (1 - 10^(-n))^d` where n is pattern length and d is digits searched

### Performance

The batch search optimization provides ~100x speedup for large lists of names by reading files once instead of N times.

## Requirements

- Python 3.10+
- `tqdm` for progress bars
- ~200GB disk space for pi digits
- Patience (searching takes a while!)

Install dependencies:
```bash
pip install tqdm
```

---

## Previous Attempts

The `previous attempts/` folder contains earlier iterations of this project before arriving at the final solution:

**[find_my_name_mp.py](previous%20attempts/find_my_name_mp.py)**
First attempt using `mpmath` to compute pi digits on-the-fly. Limited to ~10 million digits due to memory constraints when generating pi computationally.

**[find_my_name_precompute.py](previous%20attempts/find_my_name_precompute.py)**
Improvement that loads pre-computed pi digits from a file (`pi_billion.txt`) instead of computing them. Uses Python's built-in string search (Boyer-Moore algorithm).

**[download_pi_api.py](previous%20attempts/download_pi_api.py)**
Attempted to download 50 billion digits from Google's Pi API (`https://api.pi.delivery/v1/pi`) in 1-million digit chunks. Would have taken too long for large downloads.

**[download_pi.sh](previous%20attempts/download_pi.sh)**
Earlier download script targeting pi2e.ch for 50 billion digits in 10-billion digit chunks. Superseded by the archive.org approach which provides larger files.

**[count_digits.py](previous%20attempts/count_digits.py)**
Simple utility to count the number of characters in a pi digit file.

**[test_pi_file.py](previous%20attempts/test_pi_file.py)**
Test script to verify pi files loaded correctly by checking that "14159" appears at the expected position.

#!/bin/bash

# Download script for 50 billion digits of pi from pi2e.ch
# Files are split into 10 billion digit chunks

PI_DIR="/Users/kouverbingham/development/python/math/find_my_name_in_pi/pi_data"
mkdir -p "$PI_DIR"
cd "$PI_DIR"

echo "================================================"
echo "Downloading 50 billion digits of pi"
echo "This will download ~25GB compressed (~50GB uncompressed)"
echo "================================================"
echo ""

# The pi2e.ch site hosts files in chunks
# Each file contains 10 billion digits
BASE_URL="https://pi2e.ch/blog/wp-content/uploads/2017/03"

# Files for first 50 billion digits
FILES=(
    "pi_dec_1t_01.zip"  # 0-10 billion
    "pi_dec_1t_02.zip"  # 10-20 billion
    "pi_dec_1t_03.zip"  # 20-30 billion
    "pi_dec_1t_04.zip"  # 30-40 billion
    "pi_dec_1t_05.zip"  # 40-50 billion
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file already exists, skipping..."
    else
        echo "Downloading $file..."
        curl -L -O --progress-bar "$BASE_URL/$file"
    fi
done

echo ""
echo "================================================"
echo "Downloads complete! Now extracting..."
echo "================================================"

for file in "${FILES[@]}"; do
    txt_file="${file%.zip}.txt"
    if [ -f "$txt_file" ]; then
        echo "✓ $txt_file already extracted, skipping..."
    else
        echo "Extracting $file..."
        unzip -o "$file"
    fi
done

echo ""
echo "================================================"
echo "All done! Files are in: $PI_DIR"
echo "================================================"
ls -lh *.txt 2>/dev/null || echo "No .txt files found yet"

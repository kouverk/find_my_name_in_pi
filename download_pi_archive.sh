#!/bin/bash

# Download pi digits from archive.org
# RESUMABLE - if it fails, just run again!

PI_DIR="/Users/kouverbingham/development/python/math/pi/pi_data"
mkdir -p "$PI_DIR"
cd "$PI_DIR"

echo "================================================"
echo "Downloading pi digits from archive.org"
echo ""
echo "TIP: Keep your computer awake!"
echo "  caffeinate -i ./download_pi_archive.sh"
echo "================================================"
echo ""

BASE_URL="https://archive.org/download/pi_dec_1t"

# Files to download (each is 100 billion digits)
FILES=(
    "pi_dec_1t_01.zip"
    "pi_dec_1t_02.zip"
)

for FILE in "${FILES[@]}"; do
    TXT_FILE="${FILE%.zip}.txt"

    # Skip if already extracted
    if [ -f "$TXT_FILE" ]; then
        SIZE=$(stat -f%z "$TXT_FILE" 2>/dev/null || stat -c%s "$TXT_FILE" 2>/dev/null)
        if [ "$SIZE" -gt 90000000000 ]; then
            echo "✓ $TXT_FILE already exists ($SIZE bytes), skipping..."
            continue
        fi
    fi

    echo "Downloading $FILE..."
    curl -C - -L -O --progress-bar --retry 10 --retry-delay 5 "$BASE_URL/$FILE"

    # Check download
    ACTUAL_SIZE=$(stat -f%z "$FILE" 2>/dev/null || stat -c%s "$FILE" 2>/dev/null)
    if [ "$ACTUAL_SIZE" -lt 40000000000 ]; then
        echo "⚠️  Download incomplete. Run again to resume."
        exit 1
    fi

    echo "Extracting $FILE..."
    unzip -o "$FILE"
    echo "✓ Done with $FILE"
    echo ""
done

echo "================================================"
echo "✓ All downloads complete!"
echo "================================================"
ls -lh *.txt 2>/dev/null

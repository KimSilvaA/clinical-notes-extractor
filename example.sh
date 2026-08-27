#!/bin/bash
# Step 1: get filenames
./get_filenames.sh > files.txt

# Step 2: download selected files
while IFS= read -r file; do
    wget "https://example.com/$file"
done < files.txt
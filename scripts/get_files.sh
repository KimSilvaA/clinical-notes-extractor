#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILE_NAMES="$SCRIPT_DIR/../config/data_files.txt"
DEST_CSV="$SCRIPT_DIR/../src/data/raw/csv"
DEST_FHIR="$SCRIPT_DIR/../src/data/raw/fhir"

mkdir -p "$DEST_CSV" "$DEST_FHIR"

# DOWNLOAD RELEVANT CSV FILES 
while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  echo "Downloading $file ..."
  aws s3 cp --no-sign-request \
    "s3://synthea-open-data/coherent/unzipped/csv/$file" \
    "$DEST_CSV/$file"
done < "$FILE_NAMES"

# DOWNLOAD CLINICAL NOTES
aws s3 sync --no-sign-request s3://synthea-open-data/coherent/unzipped/fhir/ \
    "$DEST_FHIR"

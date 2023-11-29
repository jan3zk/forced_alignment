#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_directory output_directory"
    exit 1
fi

INPUT_DIR=$1
OUTPUT_DIR=$2

for TEI_FILE in "$INPUT_DIR"/*.xml; do
    # Extract the base filename without extension
    BASENAME=$(basename "$TEI_FILE" ".xml")
    # Construct the destination file path
    FILE_TXT="$OUTPUT_DIR/${BASENAME}-avd.txt"
	
	# Parse transcription
	python ../transcript_from_tei.py "$TEI_FILE" "$FILE_TXT" --use-norm
done
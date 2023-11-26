#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_directory output_directory"
    exit 1
fi

INPUT_DIR=$1
OUTPUT_DIR=$2

for FILE_TRS in "$INPUT_DIR"/*-std.trs; do
    # Extract the base filename without extension
    BASENAME=$(basename "$FILE_TRS" "-std.trs")
    # Construct the destination file path
    FILE_TXT="$OUTPUT_DIR/${BASENAME}-avd.txt"
	
	# Parse transcription
	python ../transcript_from_trs.py "$FILE_TRS" "$FILE_TXT"
done
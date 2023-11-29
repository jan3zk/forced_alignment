#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_directory output_directory duration"
    exit 1
fi

IN_DIR=$1
OUT_DIR=$2
DURATION=$3

for FILE_TRS in "$INPUT_DIR"/*-std.trs; do
	# Fragmentize transcription
	python ../fragmentize_trs.py "$FILE_TRS" "$OUT_DIR" "$DURATION"
done
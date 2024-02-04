#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 textgrid_dir_in textgrid_dir_out"
    exit 1
fi

# Assign input and output directories from script arguments
input_dir="$1"
output_dir="$2"

# Regular expression pattern to match numeric values in the filename
regex='_[0-9]+\.[0-9]+_'

# Iterate over all TextGrid files in the input directory
for textgrid_file in "$input_dir"/*.TextGrid; do
    # Extract base name
    base_name=$(basename "$textgrid_file")

    # Use grep to find matches and extract the first numeric value
    # This will match the first occurrence of the pattern, suitable for both filename formats
    trimmed_start=$(echo "$base_name" | grep -oE "$regex" | head -n 1 | tr -d '_')

    # Output file path
    textgrid_file_out="$output_dir/$base_name"

    # Add trimmed_start to all timing values in the TextGrid
    python compensate_trimming.py "$textgrid_file" "$trimmed_start" "$textgrid_file_out"
done

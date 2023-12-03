#!/bin/bash
source ./utils.sh

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 textgrid_dir_in textgrid_dir_out"
    exit 1
fi

# Assign input and output directories from script arguments
input_dir="$1"
output_dir="$2"

# Iterate over all TextGrid files in the input directory
for textgrid_file in "$input_dir"/*.TextGrid; do
    # Extract base name and split it to get tmin
    base_name=$(basename "$textgrid_file")
    IFS='_' read -ra NAME_PARTS <<< "$base_name"
    trimmed_start="${NAME_PARTS[1]}"

    # Output file path
    textgrid_file_out="$output_dir/$base_name"

    # Add trimmed_start to all timing values in the TextGrid
    python ../compensate_trimming.py "$textgrid_file" "$trimmed_start" "$textgrid_file_out"
done

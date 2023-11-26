#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 textgrid_dir_in trs_dir textgrid_dir_out"
    exit 1
fi

# Assign input and output directories from script arguments
input_dir="$1"
trs_dir="$2"
output_dir="$3"

# Function to extract trimmed start time from the TRS file
extract_trimmed_start() {
    awk '/<Sync time=/ { sync_time = $0; getline; if ($0 !~ /^</) { match(sync_time, /<Sync time="([0-9.]+)/, arr); print arr[1]; exit; } }' "$1"
}

# Iterate over all TRS files in the input directory
for textgrid_file in "$input_dir"/*.TextGrid; do
    # TRS file containing time stamps
    trs_file_name=$(basename "$textgrid_file")
    trs_file_name="${trs_file_name/-avd.TextGrid/-std.trs}"
    trs_file="$trs_dir/$trs_file_name"

    # Extract the start and end trim times
    trimmed_start=$(extract_trimmed_start "$trs_file")

    # Output file path
    textgrid_file_out="$output_dir/$(basename "$textgrid_file")"

    python ../compensate_trimming.py $textgrid_file $trimmed_start $textgrid_file_out
done

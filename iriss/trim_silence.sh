#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_directory output_directory"
    exit 1
fi

# Assign input and output directories from script arguments
input_dir="$1"
output_dir="$2"

# Function to convert seconds to HOURS:MM:SS.MILLISECONDS format
convert_time_format() {
    echo "$1" | awk '{
        total_seconds=$1;
        hours=int(total_seconds/3600);
        minutes=int((total_seconds%3600)/60);
        seconds=total_seconds%60;
        printf "%02d:%02d:%06.3f", hours, minutes, seconds
    }'
}

# Function to extract trimmed start time from the TRS file
extract_trimmed_start() {
    awk '/<Sync time=/ { sync_time = $0; getline; if ($0 !~ /^</) { match(sync_time, /<Sync time="([0-9.]+)/, arr); print arr[1]; exit; } }' "$1"
}

# Function to extract trimmed end time from the TRS file
extract_trimmed_end() {
    grep -oP '(?<=<Sync time=")[\d.]+' "$1" | tail -1
}

# Iterate over all TRS files in the input directory
for trs_file in "$input_dir"/*-std.trs; do
    # Extract the start and end trim times
    TRIMMED_START=$(extract_trimmed_start "$trs_file")
    TRIMMED_END=$(extract_trimmed_end "$trs_file")

    # Convert times to required format
    TRIMMED_START_FORMATTED=$(convert_time_format "$TRIMMED_START")
    TRIMMED_END_FORMATTED=$(convert_time_format "$TRIMMED_END")

    # Construct the corresponding WAV file path by replacing "-std" with "-avd"
    wav_file_name=$(basename "$trs_file")
    wav_file_name="${wav_file_name/-std.trs/-avd.wav}"
    wav_file="$input_dir/$wav_file_name"

    # Output file path
    trimmed_file="$output_dir/$(basename "${wav_file%.wav}.wav")"

    # Check if corresponding WAV file exists
    if [ -f "$wav_file" ]; then
        # Trim the WAV file using ffmpeg
        ffmpeg -i "$wav_file" -ss "$TRIMMED_START_FORMATTED" -to "$TRIMMED_END_FORMATTED" "$trimmed_file"
    else
        echo "WAV file for $trs_file not found."
    fi
done

#!/bin/bash

# Check if correct number of arguments provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    echo "Example: $0 /path/to/source/wavs /path/to/destination"
    exit 1
fi

SOURCE_DIR="$1"
DEST_DIR="$2"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory does not exist"
    exit 1
fi

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Counter for processed files
processed=0
failed=0

# Process each WAV file
for wav_file in "$SOURCE_DIR"/*.wav; do
    # Check if any wav files were found
    if [ ! -f "$wav_file" ]; then
        echo "No WAV files found in source directory"
        exit 1
    fi

    # Get the base filename
    filename=$(basename "$wav_file")
    
    # Construct the TRS filename by replacing .wav with .trs
    trs_file="${wav_file%.wav}-std.trs"
    trs_file=$(echo "$trs_file" | sed 's|/WAV/|/TRS/|')

    # Check if corresponding TRS file exists
    if [ ! -f "$trs_file" ]; then
        echo "Warning: No matching TRS file for $filename - skipping"
        ((failed++))
        continue
    fi
    
    # Construct output path
    output_file="$DEST_DIR/$filename"
    
    echo "Processing: $filename"
    
    # Run the Python script
    if python anonymize_audio.py trs "$wav_file" "$trs_file" "$output_file"; then
        echo "Successfully processed: $filename"
        ((processed++))
    else
        echo "Error processing: $filename"
        ((failed++))
    fi
done

# Print summary
echo "Processing complete!"
echo "Successfully processed: $processed files"
echo "Failed: $failed files"
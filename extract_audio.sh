#!/bin/bash

# Check if correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input_directory> <output_directory>"
  exit 1
fi

# Assign arguments to variables
INPUT_DIR="$1"
OUTPUT_DIR="$2"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Loop through all .flv and .avi files in the input directory
for file in "$INPUT_DIR"/*.{flv,avi}; do
  # Check if file exists to avoid errors when no matching files are found
  if [[ -e "$file" ]]; then
    # Get the filename without the extension
    filename=$(basename "$file" | sed 's/\.[^.]*$//')
    # Define the output file path
    output_file="$OUTPUT_DIR/$filename.wav"

    # Extract audio and convert to WAV with specified parameters
    ffmpeg -i "$file" -ar 44100 -ac 1 -acodec pcm_s16le "$output_file"
  fi
done

echo "Audio extraction complete. Files saved to $OUTPUT_DIR"

#!/bin/bash

# Check if correct number of arguments is provided
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

# Assign argument to variable
INPUT_DIR="$1"

# ... existing code ...
for file in "$INPUT_DIR"/*.{flv,avi}; do
  # Check if file exists to avoid errors when no matching files are found
  if [[ -e "$file" ]]; then
    # Get the filename without the extension
    filename=$(basename "$file" | sed 's/\.[^.]*$//')
    # Define the output file path using the same directory
    output_file="$INPUT_DIR/$filename.wav"

    # Extract audio and convert to WAV with specified parameters
    ffmpeg -i "$file" -ar 44100 -ac 1 -acodec pcm_s16le "$output_file"
  fi
done

echo "Audio extraction complete. Files saved to $INPUT_DIR"

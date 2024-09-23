#!/bin/bash

# Check if 'sox' is installed
if ! command -v sox &> /dev/null
then
    echo "Error: 'sox' is not installed. Please install it to use this script."
    exit 1
fi

# Check if directory is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Set the directory to the first argument
directory=$1

# Check if the provided argument is a valid directory
if [ ! -d "$directory" ]; then
    echo "Error: '$directory' is not a valid directory."
    exit 1
fi

# Loop through all WAV files in the provided directory
for file in "$directory"/*.wav; do
    if [ ! -f "$file" ]; then
        echo "No WAV files found in the directory '$directory'."
        exit 1
    fi

    # Use sox to get file information
    sample_rate=$(sox --i -r "$file")
    encoding=$(sox --i -e "$file")
    bit_depth=$(sox --i -b "$file")
    channels=$(sox --i -c "$file")

    # Check the properties and convert if necessary
    if [ "$sample_rate" != "44100" ] || [ "$encoding" != "Signed Integer PCM" ] || [ "$bit_depth" != "16" ] || [ "$channels" != "1" ]; then
        echo "File '$file' is not in the required format. Converting..."

        # Create a temporary output file
        temp_file="${file%.wav}_converted.wav"

        # Convert the file using sox
        sox "$file" -r 44100 -e signed-integer -b 16 -c 1 "$temp_file"

        if [ $? -eq 0 ]; then
            echo "Conversion successful. Replacing the original file."

            # Replace the original file with the converted file
            mv "$temp_file" "$file"
        else
            echo "Conversion failed for '$file'."
        fi
    else
        echo "File '$file' is already in the correct format."
    fi
done

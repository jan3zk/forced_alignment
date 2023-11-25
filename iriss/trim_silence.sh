#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_directory output_directory"
    exit 1
fi

INPUT_DIR=$1
OUTPUT_DIR=$2

# Create the output directory if it does not exist
mkdir -p "$OUTPUT_DIR"

# Silence detection parameters
SILENCE_THRESHOLD=-30dB  # Silence threshold
SILENCE_DURATION=2.0    # Duration of silence to detect in seconds
SILENCE_START_THRESHOLD=5.0

# Process each .wav file in the input directory
for FILE in "$INPUT_DIR"/*.wav; do
    # Extract filename without the path and extension
    BASENAME=$(basename "$FILE" .wav)

    # Define output file paths
    TRIMMED_FILE="$OUTPUT_DIR/${BASENAME}_trimmed.wav"
    TRIMMED_START_FILE="$OUTPUT_DIR/trim_vals/${BASENAME}_trimmed_start.txt"

    # Get the timestamps for silence periods
    FFMPEG_OUTPUT=$(ffmpeg -i "$FILE" -af silencedetect=noise=$SILENCE_THRESHOLD:d=$SILENCE_DURATION -f null - 2>&1)

    # Parse the output to get the first silence_start
    FIRST_SILENCE_START=$(echo "$FFMPEG_OUTPUT" | grep 'silence_start' | head -1 | awk -F'silence_start: ' '{print $2}' | xargs)

    # Check if the first silence_start is greater than the threshold
    if (( $(echo "$FIRST_SILENCE_START > $SILENCE_START_THRESHOLD" | bc -l) )); then
        TRIMMED_START=0
    else
        # If there is no silence or silence is within the threshold, set TRIMMED_START to the end of the first detected silence
        TRIMMED_START=$(echo "$FFMPEG_OUTPUT" | grep 'silence_end' | head -1 | awk -F'silence_end: ' '{print $2}' | awk '{print $1}' | xargs)
    fi

    # Parse the output to get the first silence_end and the last silence_start
    ##TRIMMED_START=$(echo "$FFMPEG_OUTPUT" | grep 'silence_end' | head -1 | awk '{print $5}')
    
    #TRIMMED_END=$(echo "$FFMPEG_OUTPUT" | grep 'silence_start' | tail -1 | awk '{print $5}')
    TRIMMED_END=$(echo "$FFMPEG_OUTPUT" | grep 'silence_start' | tail -1 | awk -F'silence_start: ' '{print $2}' | xargs)

    # Check if TRIMMED_START is empty or greater than TRIMMED_END
	if [ -z "$TRIMMED_START" ] || (( $(echo "$TRIMMED_START > $TRIMMED_END" | bc -l) )); then
	    TRIMMED_START=0
	fi
	
    # If no silence detected at end, set TRIMMED_END to the end of the file
    if [ -z "$TRIMMED_END" ]; then
        TRIMMED_END=$(ffprobe -i "$FILE" -show_entries format=duration -v quiet -of csv="p=0")
    fi

    # Get the total length of the WAV file
    FILE_LENGTH=$(ffprobe -i "$FILE" -show_entries format=duration -v quiet -of csv="p=0")

    # Subtract 0.5 seconds from TRIMMED_START if it's greater than 0.5 seconds
    if (( $(echo "$TRIMMED_START > 0.5" | bc -l) )); then
        TRIMMED_START=$(echo "$TRIMMED_START - 0.5" | bc -l)
    fi

    # Add 0.5 seconds to TRIMMED_END if it's less than (FILE_LENGTH - 0.5) seconds
    if (( $(echo "$TRIMMED_END + 0.5 < $FILE_LENGTH" | bc -l) )); then
        TRIMMED_END=$(echo "$TRIMMED_END + 0.5" | bc -l)
    fi

    # Trim the audio file
    ffmpeg -i "$FILE" -ss "$TRIMMED_START" -to "$TRIMMED_END" "$TRIMMED_FILE"

    # Save the TRIMMED_START value to a text file
    echo "$TRIMMED_START" > "$TRIMMED_START_FILE"

    echo "Processed $FILE"
    echo "Start Trim Timestamp: $TRIMMED_START"
	echo "End Trim Timestamp: $TRIMMED_END"
    echo "Trimmed file saved as $TRIMMED_FILE"
    echo "Start Trim Timestamp saved as $TRIMMED_START_FILE"
done

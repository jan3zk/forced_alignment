#!/bin/bash

# Check if input argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <directory_or_file_list.txt>"
  exit 1
fi

# Input is a directory
if [ -d "$1" ]; then
  DIRECTORY=$1

  # Loop through all .trs files in the directory
  for file in "$DIRECTORY"/*.trs; do
    # Check if any .trs files exist
    if [ ! -e "$file" ]; then
      echo "No .trs files found in the directory."
      exit 1
    fi

    # Extract the base name of the file (without extension)
    base_name=$(basename "$file" .trs)

    # Convert .trs file to .txt using transcriber
    transcriber -export text "$file" > "$DIRECTORY/$base_name.txt"

    echo "Converted $file to $base_name.txt"
  done

# Input is a .txt file containing a list of .trs filenames
elif [ -f "$1" ] && [[ "$1" == *.txt ]]; then
  FILE_LIST=$1

  # Loop through each line in the file list
  while IFS= read -r file; do
    # Check if the .trs file exists
    if [ ! -f "$file" ]; then
      echo "File not found: $file"
      continue
    fi

    # Extract the base name of the file (without extension)
    base_name=$(basename "$file" .trs)
    dir_name=$(dirname "$file")

    # Convert .trs file to .txt using transcriber
    transcriber -export text "$file" > "$dir_name/$base_name.txt"

    echo "Converted $file to $base_name.txt"
  done < "$FILE_LIST"

else
  echo "Error: $1 is not a valid directory or .txt file."
  exit 1
fi

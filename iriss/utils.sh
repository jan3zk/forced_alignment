# Function to extract trimmed start time from the TRS file.
# It searches for the first line that doesn't start with "<", and then
# extracts the value from the <Sync time= element that precedes that line.
extract_trimmed_start() {
    awk '
    /<Sync time=/ { 
        match($0, /<Sync time="([0-9.]+)/, arr); 
        last_sync_time = arr[1]; 
    }
    /^[^<]/ { 
        print last_sync_time; 
        exit; 
    }' "$1"
}
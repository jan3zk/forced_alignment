import sys
import os
import glob
import csv
import string
from textgrid import TextGrid, IntervalTier, Interval

# Function to load a TextGrid file
def load_textgrid(filepath):
    return TextGrid.fromFile(filepath)

# Function to check overlaps between intervals
def border_overlap(interval1, interval2):
    return (interval1.minTime <= interval2.minTime <= interval1.maxTime) or \
           (interval1.minTime <= interval2.maxTime <= interval1.maxTime)

def interval_overlap(interval1, interval2):
    # Calculate overlap start and end points
    overlap_start = max(interval1.minTime, interval2.minTime)
    overlap_end = min(interval1.maxTime, interval2.maxTime)
    
    # Calculate the duration of the overlap
    overlap_duration = max(0, overlap_end - overlap_start)
    
    # Calculate the duration of each interval
    interval1_duration = interval1.maxTime - interval1.minTime
    interval2_duration = interval2.maxTime - interval2.minTime
    
    # Calculate the minimum duration (the shorter interval)
    min_duration = min(interval1_duration, interval2_duration)
    
    # Check if the overlap is more than 95% of the shorter interval
    return overlap_duration >= 0.95 * min_duration

# Function to find all overlapping intervals between two tiers
def find_overlapping_intervals(tier1, tier2):
    concatenated_intervals = []
    
    # Iterate over each interval in tier2
    for interval2 in tier2:
        overlapping_intervals = []
        
        # Check if the interval2 overlaps with any interval in tier1
        for interval1 in tier1:
            if interval_overlap(interval1, interval2):
                overlapping_intervals.append(interval1)
        
        # If multiple intervals overlap, concatenate them (multi-word DM)
        if overlapping_intervals:
            # Find the minimum start time and maximum end time from overlapping intervals
            min_time = min(interval.minTime for interval in overlapping_intervals)
            max_time = max(interval.maxTime for interval in overlapping_intervals)
            
            # Concatenate marks from all overlapping intervals, separating by space or other delimiter
            concatenated_mark = " ".join(interval.mark for interval in overlapping_intervals if interval.mark)
            
            # Create a new concatenated interval and add it to the result
            concatenated_intervals.append(Interval(min_time, max_time, concatenated_mark))
    
    return concatenated_intervals

# Function to analyze overlaps
def analyze_overlaps(DM_tier, PU_tier):
    total_dm_count = len(DM_tier)
    match_count = 0
    
    for dm_interval in DM_tier:
        overlap_found = any(border_overlap(dm_interval, pu_interval) for pu_interval in PU_tier)
        if overlap_found:
            match_count += 1
    
    # Only record the match ratio
    match_ratio = f"{match_count}/{total_dm_count}" if total_dm_count > 0 else "0/0"
    results = (match_count, total_dm_count)
    
    return results

# Function to remove punctuation from a string
def remove_punctuation(mark):
    return mark.translate(str.maketrans('', '', string.punctuation))

# Function to process files and optionally write results to CSV
def process_files(paths):
    # Initialize cumulative statistics
    cumul_DMs = {}
    cumul_DMs['DM'] = []
    cumul_DMs['DM_af'] = []

    # Process each file
    for filepath in glob.glob(paths):
        tg = load_textgrid(filepath)
        DM_tier = tg.getFirst('discourse-marker')
        DM_tier.intervals = [interval for interval in DM_tier if interval.mark == 'POS']
        actualDM_tier = tg.getFirst('actualDM')
        actualDM_tier.intervals = [interval for interval in actualDM_tier if interval.mark == 'af']
        PU_tier = tg.getFirst('PU')
        PU_tier.intervals = [interval for interval in PU_tier if interval.mark != '']
        
        DMaf_intervals = find_overlapping_intervals(DM_tier, actualDM_tier)
        DMs = find_overlapping_intervals(tg.getFirst('strd-wrd-sgmnt'), DMaf_intervals)
        DMs = [Interval(interval.minTime, interval.maxTime, remove_punctuation(interval.mark).lower()) for interval in DMs if interval.mark != '']
        unique_DMs = set(interval.mark for interval in DMs)

        for unique_DM in unique_DMs:
            uDM_intervals = [interval for interval in DMs if interval.mark == unique_DM]
            if unique_DM not in cumul_DMs:
                cumul_DMs[unique_DM] = []
            cumul_DMs[unique_DM].append(analyze_overlaps(uDM_intervals, PU_tier))

        print(f"Overlap for {os.path.basename(filepath)}:")
        DMaf_overlap = analyze_overlaps(DMaf_intervals, PU_tier)
        cumul_DMs['DM_af'].append(DMaf_overlap)
        DM_overlap = analyze_overlaps(DM_tier, PU_tier)
        cumul_DMs['DM'].append(DM_overlap)
        print(f"  DM: {DM_overlap[0]}/{DM_overlap[1]} ({DM_overlap[0]/DM_overlap[1]:.2f})")
        print(f"  DM_af: {DMaf_overlap[0]}/{DMaf_overlap[1]} ({DMaf_overlap[0]/DMaf_overlap[1]:.2f})")

    # Display cumulative statistics
    print("\nOverlap statistics across all files:")
    for key in cumul_DMs:
        print(f"'{key}': {sum(x[0] for x in cumul_DMs[key])}/{sum(x[1] for x in cumul_DMs[key])} ({sum(x[0] for x in cumul_DMs[key])/sum(x[1] for x in cumul_DMs[key]):.2f})")
    
# Main function to handle command line arguments
if __name__ == '__main__':
    if len(sys.argv) < 1:
        print("Usage: python discourse_marker_overlap.py <path_to_textgrid_or_directory>")
        sys.exit(1)
    
    file_path_or_directory = sys.argv[1]
    process_files(file_path_or_directory)

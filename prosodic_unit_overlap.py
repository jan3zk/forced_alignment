import sys
import os
import glob
import csv
from textgrid import TextGrid

# Function to load a TextGrid file
def load_textgrid(filepath):
    return TextGrid.fromFile(filepath)

# Function to check overlaps between intervals
def interval_overlap(interval1, interval2):
    return (interval1.minTime <= interval2.minTime <= interval1.maxTime) or \
           (interval1.minTime <= interval2.maxTime <= interval1.maxTime)

# Function to analyze overlaps
def analyze_overlaps(textgrid, pos_tiers_indices, pu_tier_name):
    results = {}
    pu_tier = textgrid.getFirst(pu_tier_name)
    
    for tier_index in pos_tiers_indices:
        tier = textgrid[tier_index]
        pos_intervals = [interval for interval in tier if "POS" in interval.mark]
        total_pos_count = len(pos_intervals)
        match_count = 0
        
        for pos_interval in pos_intervals:
            overlap_found = any(interval_overlap(pos_interval, pu_interval) for pu_interval in pu_tier)
            if overlap_found:
                match_count += 1
        
        # Only record the match ratio
        match_ratio = f"{match_count}/{total_pos_count}" if total_pos_count > 0 else "0/0"
        results[tier.name] = match_ratio
    
    return results

# Function to display results in the console
def display_results(filepath, results):
    print(f"Results for {os.path.basename(filepath)}:")
    for tier, ratio in results.items():
        print(f"{tier}: {ratio}")

# Function to process files and optionally write results to CSV
def process_files(paths, output_csv=None):
    should_write_csv = output_csv is not None
    if should_write_csv:
        csvfile = open(output_csv, 'w', newline='')
        fieldnames = ['file_name', 'pitch-reset', 'intensity-reset', 'speech-rate-reduction', 'pause', 'speaker-change']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    
    for filepath in glob.glob(paths):
        tg = load_textgrid(filepath)
        results = analyze_overlaps(tg, [9, 10, 11, 12, 13], 'PU')
        
        display_results(filepath, results)  # Display results in console regardless of CSV output
        
        if should_write_csv:
            # Prepare a row for the CSV output
            csv_row = {
                'file_name': os.path.basename(filepath),
                'pitch-reset': results.get('pitch-reset', '0/0'),
                'intensity-reset': results.get('intensity-reset', '0/0'),
                'speech-rate-reduction': results.get('speech-rate-reduction', '0/0'),
                'pause': results.get('pause', '0/0'),
                'speaker-change': results.get('speaker-change', '0/0')
            }
            writer.writerow(csv_row)
    
    if should_write_csv:
        csvfile.close()

# Main function to handle command line arguments
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python prosodic_unit_overlap.py <path_to_textgrid_or_directory> [output_csv]")
        sys.exit(1)
    
    file_path_or_directory = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    process_files(file_path_or_directory, output_csv)

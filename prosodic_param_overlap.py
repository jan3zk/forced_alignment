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
        results[tier.name] = (match_count, total_pos_count)
    
    return results

# Function to display results in the console
def display_results(filepath, results):
    print(f"Overlap for {os.path.basename(filepath)}:")
    for tier, (match_count, total_pos_count) in results.items():
        print(f"  {tier}: {match_count}/{total_pos_count} ({match_count/total_pos_count:.2f})" if total_pos_count != 0 else \
              f"  {tier}: {match_count}/{total_pos_count} (N/A)")

# Function to process files and optionally write results to CSV
def process_files(paths, output_csv=None):
    should_write_csv = output_csv is not None
    if should_write_csv:
        csvfile = open(output_csv, 'w', newline='')
        fieldnames = ['file_name', 'pitch-reset', 'intensity-reset', 'speech-rate-reduction', 'pause', 'speaker-change']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    
    # Initialize cumulative statistics
    cumulative_stats = {
        'pitch-reset': [0, 0],
        'intensity-reset': [0, 0],
        'speech-rate-reduction': [0, 0],
        'pause': [0, 0],
        'speaker-change': [0, 0]
    }

    # Process each file
    for filepath in glob.glob(paths):
        tg = load_textgrid(filepath)
        results = analyze_overlaps(tg, [9, 10, 11, 12, 13], 'PU')
        
        display_results(filepath, results)  # Display results in console regardless of CSV output
        
        # Update cumulative statistics
        for tier_name, (match_count, total_pos_count) in results.items():
            if tier_name in cumulative_stats:
                cumulative_stats[tier_name][0] += match_count
                cumulative_stats[tier_name][1] += total_pos_count
        
        if should_write_csv:
            # Prepare a row for the CSV output
            csv_row = {
                'file_name': os.path.basename(filepath),
                'pitch-reset': f"{results.get('pitch-reset', (0, 0))[0]}/{results.get('pitch-reset', (0, 0))[1]}",
                'intensity-reset': f"{results.get('intensity-reset', (0, 0))[0]}/{results.get('intensity-reset', (0, 0))[1]}",
                'speech-rate-reduction': f"{results.get('speech-rate-reduction', (0, 0))[0]}/{results.get('speech-rate-reduction', (0, 0))[1]}",
                'pause': f"{results.get('pause', (0, 0))[0]}/{results.get('pause', (0, 0))[1]}",
                'speaker-change': f"{results.get('speaker-change', (0, 0))[0]}/{results.get('speaker-change', (0, 0))[1]}"
            }
            writer.writerow(csv_row)
    
    if should_write_csv:
        csvfile.close()

    # Display cumulative statistics
    print("\nCumulative statistics across all files:")
    for tier_name, (cumulative_match, cumulative_total) in cumulative_stats.items():
        if cumulative_total > 0:
            # Calculate match ratio
            match_ratio = f"{cumulative_match}/{cumulative_total}"
            match_percentage = (cumulative_match / cumulative_total)# * 100

            # Calculate non-match ratio
            non_match = cumulative_total - cumulative_match
            non_match_ratio = f"{non_match}/{cumulative_total}"
            non_match_percentage = (non_match / cumulative_total)# * 100

            # Print the results
            print(f"{tier_name}:")
            print(f"  Overlapping: {match_ratio} ({match_percentage:.2f})")
            print(f"  Non-overlapping: {non_match_ratio} ({non_match_percentage:.2f})")
        else:
            # If no intervals are found, handle it gracefully
            print(f"{tier_name}: No intervals found (0/0)")


# Main function to handle command line arguments
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python prosodic_param_overlap.py <path_to_textgrid_or_directory> [output_csv]")
        sys.exit(1)
    
    file_path_or_directory = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    process_files(file_path_or_directory, output_csv)

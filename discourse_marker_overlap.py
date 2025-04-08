import sys
import os
import glob
from textgrid import TextGrid
from collections import defaultdict, Counter

def load_textgrid(filepath):
    return TextGrid.fromFile(filepath)

def clean_label(label):
    """Clean label by removing Unicode control characters."""
    # List of Unicode control characters to remove
    control_chars = ['\u202E']  # Right-to-Left Override
    
    # Remove each control character from the label
    for char in control_chars:
        label = label.replace(char, '')
    
    return label

def get_group_from_label(label):
    """Extract main group (TI, TQ, TR, I, C, ...) from classification label."""
    if not label or '-' not in label:
        return None
    label = clean_label(label.upper())
    return label.split('-')[0]

def get_subgroup_from_label(label):
    """Extract subgroup from classification label."""
    if not label or '-' not in label:
        return None
    label = clean_label(label.upper())
    return label.split('-')[1]

def check_boundary_overlap(interval1, interval2):
    """Check if intervals share any boundary points."""
    threshold = 0.01  # 10ms threshold for boundary matching
    return (interval1.minTime <= interval2.minTime <= interval1.maxTime) or \
           (interval1.minTime <= interval2.maxTime <= interval1.maxTime) or \
           (interval1.maxTime - threshold <= interval2.minTime <= interval1.maxTime + threshold) or \
           (interval1.minTime - threshold <= interval2.maxTime <= interval1.minTime + threshold)

def check_interval_overlap(interval1, interval2):
    """Check if intervals overlap substantially."""
    return (interval1.minTime <= interval2.maxTime and interval2.minTime <= interval1.maxTime)

def check_significant_overlap(interval1, interval2):
    """Check if two intervals have significant overlap (>50%)."""
    if not (interval1.minTime <= interval2.maxTime and interval2.minTime <= interval1.maxTime):
        return False
    
    overlap_start = max(interval1.minTime, interval2.minTime)
    overlap_end = min(interval1.maxTime, interval2.maxTime)
    
    overlap_duration = overlap_end - overlap_start
    interval2_duration = interval2.maxTime - interval2.minTime
    
    # Check if overlap is significant relative to the word interval
    return interval2_duration > 0 and (overlap_duration / interval2_duration) > 0.5

def extract_discourse_markers(textgrid):
    """
    Extract discourse markers from strd-wrd-sgmnt tier and their classifications.
    Properly handles multi-word discourse markers without capturing adjacent words.
    
    Returns:
    - dict: Dictionary mapping group/subgroup to list of marker words with frequencies
    """
    try:
        # Get required tiers
        strd_wrd_sgmnt_tier = textgrid.getFirst('strd-wrd-sgmnt')
        actualDM_tier = textgrid.getFirst('actualDM')
        classif_tier = textgrid.getFirst('actual-DM-classif')
        
        if not strd_wrd_sgmnt_tier or not actualDM_tier or not classif_tier:
            print("Required tiers not found in TextGrid")
            return {}, {}
        
        # Dictionaries to store markers by group and subgroup
        group_markers = defaultdict(Counter)
        subgroup_markers = defaultdict(Counter)
        
        # Find all intervals with "af" marks in actualDM tier
        for dm_interval in actualDM_tier:
            if dm_interval.mark != "af":
                continue
            
            # Find corresponding classification interval for more precise boundaries
            classif_interval = None
            for interval in classif_tier:
                if check_interval_overlap(dm_interval, interval) and interval.mark:
                    classif_interval = interval
                    break
            
            if not classif_interval:
                continue
                
            # Get classification information
            classification = classif_interval.mark
            group = get_group_from_label(classification)
            subgroup = get_subgroup_from_label(classification)
            
            if not group and not subgroup:
                continue
                
            # Find all word intervals that have significant overlap with the classification interval
            overlapping_words = []
            for word_interval in strd_wrd_sgmnt_tier:
                if word_interval.mark.strip() and check_significant_overlap(classif_interval, word_interval):
                    overlapping_words.append(word_interval)
            
            # Sort by start time to ensure correct word order
            overlapping_words.sort(key=lambda x: x.minTime)
            
            # Concatenate to form the complete marker
            if not overlapping_words:
                continue
                
            marker_parts = [interval.mark.strip() for interval in overlapping_words]
            marker_text = " ".join(marker_parts)
            
            # Strip punctuation at the end of the marker
            marker_text = marker_text.rstrip('.,;:!?"\'')\
            
            # Store original casing but use lowercase for counting (case insensitive)
            marker_text_lower = marker_text.lower()
            
            # Update counters
            if group:
                group_markers[group][marker_text_lower] += 1
            if subgroup:
                subgroup_markers[subgroup][marker_text_lower] += 1
        
        return group_markers, subgroup_markers
        
    except Exception as e:
        print(f"Error extracting discourse markers: {str(e)}")
        return {}, {}

def analyze_overlaps(pu_tier, classif_tier):
    """Analyze overlaps between classification labels and prosodic unit boundaries."""
    try:
        group_overlaps = defaultdict(int)
        subgroup_overlaps = defaultdict(int)
        group_totals = defaultdict(int)
        subgroup_totals = defaultdict(int)
        full_labels = defaultdict(str)  # Store full label for each subgroup
        
        # First count total occurrences and check for overlaps
        for classif_interval in classif_tier:
            if not classif_interval.mark:
                continue
            
            cleaned_mark = clean_label(classif_interval.mark)
            
            group = get_group_from_label(cleaned_mark)
            subgroup = get_subgroup_from_label(cleaned_mark)
            
            # Count totals
            if group:
                group_totals[group] += 1
            if subgroup:
                subgroup_totals[subgroup] += 1
                full_labels[subgroup] = cleaned_mark.upper()
            
            # Check for overlap with any PU boundary
            has_overlap = False
            for pu_interval in pu_tier:
                if not pu_interval.mark:
                    continue
                
                if check_boundary_overlap(classif_interval, pu_interval):
                    has_overlap = True
                    break  # Found an overlap, no need to check other PU intervals
            
            # If overlap found, increment counters
            if has_overlap:
                if group:
                    group_overlaps[group] += 1
                if subgroup:
                    subgroup_overlaps[subgroup] += 1
        
        return group_overlaps, group_totals, subgroup_overlaps, subgroup_totals, full_labels
    
    except Exception as e:
        print(f"Error during overlap analysis: {str(e)}")
        return None, None, None, None, None

def analyze_dm_overlaps(pu_tier, dm_tier):
    """Analyze overlaps between actualDM 'af' marks and PU boundaries."""
    overlaps = 0
    total = 0
    
    # Iterate through DM intervals
    for dm_interval in dm_tier:
        if dm_interval.mark != "af":
            continue
            
        total += 1
        # Check for overlap with any PU boundary
        for pu_interval in pu_tier:
            if not pu_interval.mark:
                continue
                
            if check_boundary_overlap(dm_interval, pu_interval):
                overlaps += 1
                break  # Count only once per DM interval
                    
    return overlaps, total

def format_ratio(overlaps, total):
    """Format overlap ratio as string with percentage."""
    if total == 0:
        return "0/0 (0.0%)"
    percentage = (overlaps / total) * 100
    return f"{overlaps}/{total} ({percentage:.1f}%)"

def process_files(paths):
    total_group_overlaps = defaultdict(int)
    total_group_counts = defaultdict(int)
    total_subgroup_overlaps = defaultdict(int)
    total_subgroup_counts = defaultdict(int)
    total_dm_overlaps = 0
    total_dm_count = 0
    processed_files = 0
    skipped_files = 0
    full_labels = {}  # Store full labels across all files
    
    # Dictionaries to store total markers by group and subgroup
    total_group_markers = defaultdict(Counter)
    total_subgroup_markers = defaultdict(Counter)
    
    for filepath in glob.glob(paths):
        print(f"\nProcessing file: {os.path.basename(filepath)}")
        
        # Load TextGrid file
        tg = load_textgrid(filepath)
        if tg is None:
            print(f"Skipping file {filepath}")
            skipped_files += 1
            continue
            
        try:
            # Get required tiers
            pu_tier = tg.getFirst('PU')
            classif_tier = tg.getFirst('actual-DM-classif')
            dm_tier = tg.getFirst('actualDM')
            
            if not pu_tier or not classif_tier or not dm_tier:
                print(f"Required tiers not found in {filepath}")
                skipped_files += 1
                continue
            
            # Analyze classification overlaps
            results = analyze_overlaps(pu_tier, classif_tier)
            if results == (None, None, None, None, None):
                print(f"Error analyzing overlaps in {filepath}")
                skipped_files += 1
                continue
                
            group_overlaps, group_totals, subgroup_overlaps, subgroup_totals, file_labels = results
            
            # Update full_labels with new labels from this file
            for subgroup, label in file_labels.items():
                if subgroup not in full_labels:
                    full_labels[subgroup] = label
            
            # Analyze DM overlaps
            dm_overlaps, dm_count = analyze_dm_overlaps(pu_tier, dm_tier)
            total_dm_overlaps += dm_overlaps
            total_dm_count += dm_count
            
            # Extract discourse markers and their classifications
            group_markers, subgroup_markers = extract_discourse_markers(tg)
            
            # Print discourse markers for this file
            print("\nDiscourse markers by group:")
            for group, markers in sorted(group_markers.items()):
                marker_strings = [f"'{marker}' ({count})" for marker, count in markers.most_common()]
                print(f"- Group {group}: {', '.join(marker_strings)}")
            
            print("\nDiscourse markers by subgroup:")
            for subgroup, markers in sorted(subgroup_markers.items()):
                if subgroup in file_labels:
                    marker_strings = [f"'{marker}' ({count})" for marker, count in markers.most_common()]
                    print(f"- {file_labels[subgroup]}: {', '.join(marker_strings)}")
            
            # Update total marker counts
            for group, markers in group_markers.items():
                total_group_markers[group].update(markers)
            
            for subgroup, markers in subgroup_markers.items():
                total_subgroup_markers[subgroup].update(markers)
            
            # Add to totals
            for group in group_totals:
                total_group_overlaps[group] += group_overlaps[group]
                total_group_counts[group] += group_totals[group]
            for subgroup in subgroup_totals:
                total_subgroup_overlaps[subgroup] += subgroup_overlaps[subgroup]
                total_subgroup_counts[subgroup] += subgroup_totals[subgroup]
            
            # Print results for this file
            print("\nActualDM overlaps:")
            print(f"- 'af' marks: {format_ratio(dm_overlaps, dm_count)}")
            
            print("\nGroup overlaps:")
            for group in sorted(group_totals.keys()):
                ratio = format_ratio(group_overlaps[group], group_totals[group])
                print(f"- Group {group}: {ratio}")
                
            print("\nSubgroup overlaps:")
            for subgroup in sorted(subgroup_totals.keys()):
                ratio = format_ratio(subgroup_overlaps[subgroup], subgroup_totals[subgroup])
                print(f"- {file_labels[subgroup]}: {ratio}")
                
            processed_files += 1
            
        except Exception as e:
            print(f"Error processing file {filepath}: {str(e)}")
            skipped_files += 1
            continue
    
    # Print total results
    print(f"\nProcessed {processed_files} files successfully")
    if skipped_files > 0:
        print(f"Skipped {skipped_files} files due to errors")
        
    print("\nTotal results across all files:")
    
    print("\nActualDM overlaps:")
    print(f"- 'af' marks: {format_ratio(total_dm_overlaps, total_dm_count)}")
    
    print("\nGroup overlaps:")
    for group in sorted(total_group_counts.keys()):
        ratio = format_ratio(total_group_overlaps[group], total_group_counts[group])
        print(f"- Group {group}: {ratio}")
        
    print("\nSubgroup overlaps:")
    for subgroup in sorted(total_subgroup_counts.keys()):
        ratio = format_ratio(total_subgroup_overlaps[subgroup], total_subgroup_counts[subgroup])
        print(f"- {full_labels[subgroup]}: {ratio}")
    
    # Print total discourse markers
    print("\nTotal discourse markers by group:")
    for group, markers in sorted(total_group_markers.items()):
        marker_strings = [f"'{marker}' ({count})" for marker, count in markers.most_common()]
        print(f"\nGroup {group} markers (total: {sum(markers.values())}): {', '.join(marker_strings)}")
    
    print("\nTotal discourse markers by subgroup:")
    for subgroup, markers in sorted(total_subgroup_markers.items()):
        if subgroup in full_labels:
            marker_strings = [f"'{marker}' ({count})" for marker, count in markers.most_common()]
            print(f"\n{full_labels[subgroup]} markers (total: {sum(markers.values())}): {', '.join(marker_strings)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python discourse_marker_overlap.py <path_to_textgrid_s>")
        sys.exit(1)
    file_path_or_directory = sys.argv[1]
    process_files(file_path_or_directory)
import sys
import os
import glob
from textgrid import TextGrid
from collections import defaultdict

def load_textgrid(filepath):
    return TextGrid.fromFile(filepath)

def get_group_from_label(label):
    """Extract main group (TI, TQ, TR, I, C, ...) from classification label."""
    if not label or '-' not in label:
        return None
    label = label.upper()
    return label.split('-')[0]
#    if not label:
#        return None
#    label = label.upper()
#    parts = label.split('-')
#    if len(parts) < 1:
#        return None
#    main_part = parts[0]
#    if main_part.startswith('T'):
#        return main_part[:2]
#    return main_part[0]

def get_subgroup_from_label(label):
    """Extract subgroup from classification label."""
    if not label or '-' not in label:
        return None
    label = label.upper()
    return label.split('-')[1]

def check_boundary_overlap(interval1, interval2):
    """Check if intervals share any boundary points."""
    threshold = 0.01  # 10ms threshold for boundary matching
    return (abs(interval1.maxTime - interval2.maxTime) < threshold or
            abs(interval1.minTime - interval2.minTime) < threshold or
            abs(interval1.maxTime - interval2.minTime) < threshold or
            abs(interval1.minTime - interval2.maxTime) < threshold)

def analyze_dm_overlaps(pu_tier, dm_tier):
    """Analyze overlaps between actualDM 'af' marks and PU boundaries."""
    overlaps = 0
    total = 0
    
    # Count total 'af' occurrences
    for dm_interval in dm_tier:
        if dm_interval.mark == "af":
            total += 1
            # Check for overlap with any PU boundary
            for pu_interval in pu_tier:
                if not pu_interval.mark:
                    continue
                if check_boundary_overlap(dm_interval, pu_interval):
                    overlaps += 1
                    break  # Count only once per DM interval
                    
    return overlaps, total

def analyze_overlaps(pu_tier, classif_tier):
    """Analyze overlaps between classification labels and prosodic unit boundaries."""
    try:
        group_overlaps = defaultdict(int)
        subgroup_overlaps = defaultdict(int)
        group_totals = defaultdict(int)
        subgroup_totals = defaultdict(int)
        
        # First count total occurrences
        for classif_interval in classif_tier:
            if not classif_interval.mark:
                continue
            
            group = get_group_from_label(classif_interval.mark)
            if group:
                group_totals[group] += 1
                
            subgroup = get_subgroup_from_label(classif_interval.mark)
            if subgroup:
                subgroup_totals[subgroup] += 1
        
        # Then count overlaps
        for pu_interval in pu_tier:
            if not pu_interval.mark:
                continue
                
            for classif_interval in classif_tier:
                if not classif_interval.mark:
                    continue
                    
                if check_boundary_overlap(classif_interval, pu_interval):
                    group = get_group_from_label(classif_interval.mark)
                    if group:
                        group_overlaps[group] += 1
                        
                    subgroup = get_subgroup_from_label(classif_interval.mark)
                    if subgroup:
                        subgroup_overlaps[subgroup] += 1
        
        return group_overlaps, group_totals, subgroup_overlaps, subgroup_totals
    
    except Exception as e:
        print(f"Error during overlap analysis: {str(e)}")
        return None, None, None, None

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
            if results == (None, None, None, None):
                print(f"Error analyzing overlaps in {filepath}")
                skipped_files += 1
                continue
                
            group_overlaps, group_totals, subgroup_overlaps, subgroup_totals = results
            
            # Analyze DM overlaps
            dm_overlaps, dm_count = analyze_dm_overlaps(pu_tier, dm_tier)
            total_dm_overlaps += dm_overlaps
            total_dm_count += dm_count
            
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
                print(f"- Subgroup {subgroup}: {ratio}")
                
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
        print(f"- Subgroup {subgroup}: {ratio}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python discourse_marker_overlap.py <path_to_textgrid_s>")
        sys.exit(1)
    file_path_or_directory = sys.argv[1]
    process_files(file_path_or_directory)

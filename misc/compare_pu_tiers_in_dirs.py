import os
import sys
from textgrid import TextGrid

def get_pu_intervals(textgrid_path):
    """
    Load the TextGrid, find the tier named 'PU',
    and return a list of (start, end, label) tuples.
    """
    tg = TextGrid.fromFile(textgrid_path)
    for tier in tg:
        # match 'PU' tier name (case-insensitive)
        if tier.name.strip().lower() == 'pu':
            if hasattr(tier, 'intervals'):
                # IntervalTier
                return [(i.minTime, i.maxTime, i.mark) for i in tier.intervals]
            elif hasattr(tier, 'points'):
                # TextTier (less likely for prosodic units, but just in case)
                return [(p.time, p.time, p.mark) for p in tier.points]
    # If we don't find a tier named 'PU', return an empty list
    return []

def compare_pu_intervals(intervals1, intervals2, time_tolerance=0.0001):
    """
    Compare two lists of (start, end, label) tuples from 'PU' tiers.
    Checks for overlapping intervals and label mismatches.
    
    Returns a list of textual differences describing mismatches or changes.
    """
    differences = []
    i, j = 0, 0
    while i < len(intervals1) and j < len(intervals2):
        start1, end1, label1 = intervals1[i]
        start2, end2, label2 = intervals2[j]

        # Check if intervals overlap (allow for a small tolerance)
        overlap = not (end1 < start2 - time_tolerance or end2 < start1 - time_tolerance)
        if overlap:
            # If they overlap, compare the labels
            if label1 != label2:
                differences.append(
                    f"Overlap between [{start1:.2f}, {end1:.2f}] and "
                    f"[{start2:.2f}, {end2:.2f}]: labels differ: '{label1}' vs. '{label2}'"
                )

        # Move on to the next interval(s), whichever ends first
        if end1 < end2:
            i += 1
        elif end2 < end1:
            j += 1
        else:
            i += 1
            j += 1

    return differences

def compare_pu_tiers(textgrid1, textgrid2):
    """
    Load the 'PU' tier intervals from two TextGrids and compare them.
    Returns a list of differences or an explanation if 'PU' is missing.
    """
    pu_intervals_1 = get_pu_intervals(textgrid1)
    pu_intervals_2 = get_pu_intervals(textgrid2)

    # If we don't find PU in one or both
    if not pu_intervals_1 and not pu_intervals_2:
        return [f"No 'PU' tier found in both files:\n  {textgrid1}\n  {textgrid2}"]
    elif not pu_intervals_1:
        return [f"No 'PU' tier found in: {textgrid1}"]
    elif not pu_intervals_2:
        return [f"No 'PU' tier found in: {textgrid2}"]

    differences = compare_pu_intervals(pu_intervals_1, pu_intervals_2)
    return differences

def get_textgrid_files_by_prefix(directory, prefix_length=21):
    """
    Returns a dict mapping the first `prefix_length` characters of the filename
    to a list of full filenames that share that prefix.
    Only includes .TextGrid files (case-insensitive).
    """
    mapping = {}
    for fname in os.listdir(directory):
        full_path = os.path.join(directory, fname)
        if not os.path.isfile(full_path):
            continue
        if not fname.lower().endswith('.textgrid'):
            continue
        # Use only the first 21 characters as the key
        key_prefix = fname[:prefix_length]
        mapping.setdefault(key_prefix, []).append(fname)
    return mapping

if __name__ == "__main__":
    # Usage:
    #   python compare_pu_tiers_in_dirs.py /path/to/dir1 /path/to/dir2
    # The script will compare all pairs of files that share the same
    # first 21 characters in their filename.

    if len(sys.argv) != 3:
        print("Usage: python compare_pu_tiers_in_dirs.py <Dir1> <Dir2>")
        sys.exit(1)

    dir1 = sys.argv[1]
    dir2 = sys.argv[2]

    if not os.path.isdir(dir1) or not os.path.isdir(dir2):
        print("One or both of the provided paths are not directories.")
        sys.exit(1)

    # Build dictionaries: prefix -> list of files
    prefix_length = 21
    files_by_prefix_dir1 = get_textgrid_files_by_prefix(dir1, prefix_length)
    files_by_prefix_dir2 = get_textgrid_files_by_prefix(dir2, prefix_length)

    # Find all common prefixes
    common_prefixes = set(files_by_prefix_dir1.keys()).intersection(
        files_by_prefix_dir2.keys()
    )

    if not common_prefixes:
        print("No common prefixes (first 21 characters) found between directories.")
        sys.exit(0)

    # Optionally, report prefixes unique to each directory
    unique_dir1 = set(files_by_prefix_dir1.keys()) - common_prefixes
    unique_dir2 = set(files_by_prefix_dir2.keys()) - common_prefixes
    if unique_dir1:
        print(f"Prefixes only in {dir1}: {unique_dir1}")
    if unique_dir2:
        print(f"Prefixes only in {dir2}: {unique_dir2}")

    # Compare all pairs of files that share the same prefix
    for prefix in sorted(common_prefixes):
        dir1_files = files_by_prefix_dir1[prefix]
        dir2_files = files_by_prefix_dir2[prefix]

        for f1 in dir1_files:
            for f2 in dir2_files:
                path1 = os.path.join(dir1, f1)
                path2 = os.path.join(dir2, f2)
                diffs = compare_pu_tiers(path1, path2)

                if diffs:
                    print(f"\nComparing prefix '{prefix}' -> '{f1}' vs '{f2}':")
                    for d in diffs:
                        print(" -", d)
                else:
                    print(f"\nComparing prefix '{prefix}' -> '{f1}' vs '{f2}': No differences in 'PU' tier.")

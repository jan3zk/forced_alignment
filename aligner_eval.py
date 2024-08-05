import os
import re
import glob
import string
import xml.etree.ElementTree as ET
from utils_tei import timings
from textgrid import TextGrid, IntervalTier, Interval
import pandas as pd
import numpy as np
import csv
import argparse

def extract_intervals(in_filepath):
    word_intervals = []

    if in_filepath.endswith(".xml"):
        tree = ET.parse(in_filepath)
        root = tree.getroot()
        time_list = timings(root)
        namespaces = {'ns': 'http://www.tei-c.org/ns/1.0'}

        for elem in root.iter():
            if elem.tag in [f'{{{namespaces["ns"]}}}w', f'{{{namespaces["ns"]}}}pc']:
                word_start, word_end = None, None
                if elem.get('synch'):
                    word_synch = elem.attrib["synch"][1:]
                    word_start = next((num for str_, num in time_list if str_ == word_synch), None)
                    word_end = next((time_list[i+1][1] for i in range(len(time_list)-1) if time_list[i][0] == word_synch), None)
                if elem.text:
                    word_intervals.append((word_start, word_end, elem.text))

    elif in_filepath.endswith(".TextGrid"):
        tg = TextGrid.fromFile(in_filepath)
        word_intervals = tg.getFirst("strd-wrd-sgmnt")
        word_intervals = [(interval.minTime, interval.maxTime, interval.mark) for interval in word_intervals]

    elif in_filepath.endswith(".ctm"):
        df = pd.read_csv(in_filepath, delimiter=' ', header=None, quoting=csv.QUOTE_NONE)
        word_intervals = df.iloc[:, 2:5]
        word_intervals = list(word_intervals.itertuples(index=False, name=None))

    if word_intervals:
        # Remove intervals where the last element (word) is empty or contains only whitespace
        word_intervals = [interval for interval in word_intervals if interval[-1].strip()]
        # Remove intervals containing anonymized words, identified by square brackets
        word_intervals = [interval for interval in word_intervals if not ('[' in interval[-1] and ']' in interval[-1])]
        # Remove intervals containing only punctuation characters
        word_intervals = [t for t in word_intervals if t[-1].replace('"', '') not in string.punctuation]
        # Remove intervals containing only ellipsis ('…' or '...')
        word_intervals = [t for t in word_intervals if t[-1] != '…' and t[-1] != '...']
        # Remove intervals where the last element (word) contains only escape sequences (whitespace, newline, tab, etc.)
        word_intervals = [t for t in word_intervals if not re.match(r'^[\s\r\n\t]*$', t[-1])]

    return word_intervals

def calculate_tolerance_ratio(differences, tolerance):
    # Calculate the ratio of files within a specific tolerance
    within_tolerance = [diff <= tolerance for diff in differences]
    ratio = sum(within_tolerance) / len(within_tolerance)
    return ratio

def extract_filenames(file_paths):
    """Extract filenames without extensions from a list of file paths."""
    filenames = set()
    for path in file_paths:
        filename = os.path.splitext(os.path.basename(path))[0]
        filenames.add(filename)
    return filenames

def intersection_of_filenames(lists_of_file_paths):
    """Find intersection of filenames (without extensions) from multiple lists of file paths."""
    if not lists_of_file_paths:
        return set()
    
    # Initialize intersection set with the first list
    intersection_set = extract_filenames(lists_of_file_paths[0])
    
    # Intersect with filenames from subsequent lists
    for file_paths in lists_of_file_paths[1:]:
        filenames_set = extract_filenames(file_paths)
        intersection_set.intersection_update(filenames_set)
    
    return intersection_set

def compute_averages(list_of_lists):
    # Determine the length of the inner lists
    inner_list_length = len(list_of_lists[0])
    
    # Initialize lists to store sums and counts of the first and second elements of tuples
    sum_first_elements = [0] * inner_list_length
    sum_second_elements = [0] * inner_list_length
    count_first_elements = [0] * inner_list_length
    count_second_elements = [0] * inner_list_length
    
    # First pass: Compute initial averages
    for tuple_list in list_of_lists:
        for i, (first, second, _) in enumerate(tuple_list):
            if first is not None:
                sum_first_elements[i] += first
                count_first_elements[i] += 1
            if second is not None:
                sum_second_elements[i] += second
                count_second_elements[i] += 1
    
    # Compute the initial averages
    avg_first_elements = [
        (sum_first_elements[i] / count_first_elements[i]) if count_first_elements[i] > 0 else None
        for i in range(inner_list_length)
    ]
    avg_second_elements = [
        (sum_second_elements[i] / count_second_elements[i]) if count_second_elements[i] > 0 else None
        for i in range(inner_list_length)
    ]
    
    # Reset sums and counts for the second pass
    sum_first_elements = [0] * inner_list_length
    count_first_elements = [0] * inner_list_length

    # Second pass: Compute sums and counts excluding outliers
    outlier_threshold = 1
    for tuple_list in list_of_lists:
        for i, (first, _, _) in enumerate(tuple_list):
            if first is not None and abs(first - avg_first_elements[i]) <= outlier_threshold:
                sum_first_elements[i] += first
                count_first_elements[i] += 1
    
    # Compute the final averages
    avg_first_elements = [
        (sum_first_elements[i] / count_first_elements[i]) if count_first_elements[i] > 0 else None
        for i in range(inner_list_length)
    ]
    avg_second_elements = [
        (sum_second_elements[i] / count_second_elements[i]) if count_second_elements[i] > 0 else None
        for i in range(inner_list_length)
    ]
    
    # Construct the result list of tuples
    result = [(avg_first_elements[i], avg_second_elements[i], list_of_lists[0][i][2]) for i in range(inner_list_length)]
    return result

if __name__ == "__main__":
    # Call examples:
    # python aligner_eval.py "data/gos_processed/GosVL/TextGrid_final/GosVL*.TextGrid" "data/Gos.TEI.2.1/GosVL/GosVL*.xml" "data/nemo/output/GosVL/ctm/words/GosVL*.ctm"
    # python aligner_eval.py "data/nemo/output/GosVL/ctm/words/GosVL*.ctm" "data/Gos.TEI.2.1/GosVL/GosVL*.xml" "data/gos_processed/GosVL/TextGrid_final/GosVL*.TextGrid"

    parser = argparse.ArgumentParser(description='Evaluate the alignments between the test and the referece forced alignments.')
    parser.add_argument('all_intervals', nargs='+', default=[],
    help='''A list of strings representing files containing time intervals.
    First string points to test intervals, others point to reference intervals.
    If multiple reference strings are provided an average is computed over corresponding intervals.''')
    parser.add_argument('--verbose', action='store_true', help='Print detailed information')
    parser.add_argument('--csv', type=str, default=[], help='Store differences into directory defined here')

    args = parser.parse_args()
    all_intervals = args.all_intervals
    verbose = args.verbose

    # Extracting the directory and file extension for both patterns
    dirs, extensions, gt_intervals =  [], [], []
    for intervals in all_intervals:
        _dir, _extension = os.path.dirname(intervals), os.path.splitext(intervals)[1]
        dirs.append(_dir)
        extensions.append(_extension)
        gt_intervals.append(sorted([s.replace('-avd', '') for s in glob.glob(intervals)]))

    gt_files = intersection_of_filenames(gt_intervals)
    gt_files = sorted(gt_files)
    all_differences = []

    for base_name in gt_files:
        continue_outer = True
        # Construct FA filepath by matching the basename and using the FA extension
        fa_filepath = os.path.join(dirs[0], base_name + extensions[0])
        fa_filepath_avd = os.path.join(dirs[0], base_name + "-avd" + extensions[0])
        if os.path.exists(fa_filepath_avd):
            fa_filepath = fa_filepath_avd

        # Check if the FA file exists
        if not os.path.exists(fa_filepath):
            print(f"Warning: No corresponding FA file found for {gt_filepath}")
            continue
        
        GT_words = []
        for n, dir in enumerate(dirs):
            gt_filepath = os.path.join(dir, base_name + extensions[n])
            gt_filepath_avd = os.path.join(dir, base_name + "-avd" + extensions[n])
            if os.path.exists(gt_filepath_avd):
                gt_filepath = gt_filepath_avd
            try:
                GT_words.append(extract_intervals(gt_filepath))
            except Exception as e:
                print(f"Skipping {gt_filepath}. Check for overlapping inervals.")
                continue_outer = False
                break

        if continue_outer:
            if not all(len(lst) == len(GT_words[0]) for lst in GT_words):
                print(f"Warning: Skipping file {gt_filepath} since the length of GT sets differ.")
                continue
            
            if len(GT_words) > 1:
                GT_words = compute_averages(GT_words[1:])
            else:
                GT_words = GT_words[1]

            try:
                FA_words = extract_intervals(fa_filepath)
            except Exception as e:
                print(f"Skipping {fa_filepath}. Check for overlapping inervals.")
                continue
            if len(GT_words) != len(FA_words):
                print(f"Warning: Skipping file {gt_filepath} since the number of GT words is different than FA words ({len(GT_words)} != {len(FA_words)}).")
                continue

            if all(t[0] is None for t in GT_words):
                print(f"Warning: Skipping file {gt_filepath} since it has no GT annotations.")
                continue

            # Aligning and computing the differences
            aligned_words = [(t1, t2) for t1, t2 in zip(GT_words, FA_words) if None not in t1]
            GT_words, FA_words = zip(*aligned_words)
            GT_start = np.array([elem[0] for elem in GT_words])
            FA_start = np.array([elem[0] for elem in FA_words])
            differences = np.abs(GT_start - FA_start) * 1000

            if args.verbose:
                # Print largest 10 differences
                word_differences = list(zip(differences, GT_words, FA_words))
                word_differences.sort(key=lambda x: x[0], reverse=False)
                word_differences = word_differences[-9:]
                print('Largest 10 differences')
                for diff, gt_word, fa_word in word_differences:
                    print(f"Difference: {diff:.2f}ms, GT_word: {gt_word}, FA_word: {fa_word}")

            print(f"{base_name}: Mean diff. = {round(np.mean(differences), 2)}, median diff. = {round(np.median(differences), 2)}")

            # Optionally write interval starts for each word into csv
            if args.csv:
                all_data = [(a, x, c) for ((a, _, c), (x, _, _)) in zip(GT_words, FA_words)]
                with open(os.path.join(args.csv, base_name + '.csv'), 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(all_data)
            all_differences.append(differences)

    if all_differences:
        all_differences = np.hstack(all_differences)
        print(f"Overall mean difference: {round(np.mean(all_differences), 1)}")
        print(f"Overall median difference: {round(np.median(all_differences), 1)}")

        # Calculate percentages for each tolerance
        tolerances = [10, 50, 100]
        for tolerance in tolerances:
            ratio = calculate_tolerance_ratio(all_differences, tolerance)
            print(f"Ratio of boundaries within {tolerance}ms tolerance: {round(ratio, 2)}")

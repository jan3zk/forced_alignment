import os
import re
import sys
import glob
import string
import xml.etree.ElementTree as ET
from utils_tei import timings
from textgrid import TextGrid, IntervalTier, Interval
import pandas as pd
import numpy as np
import csv

def extract_GT_intervals(xml_filepath):

    # Parse the XML file
    tree = ET.parse(xml_filepath)
    root = tree.getroot()

    # Create the time lookup dictionary
    time_list = timings(root)

    # Define the TEI and XML namespaces
    namespaces = {'ns': 'http://www.tei-c.org/ns/1.0'}
    xml_ns = 'http://www.w3.org/XML/1998/namespace'

    # Initialize an empty list to store the extracted data
    word_intervals = []

    # Iterate through all elements in the XML file
    for elem in root.iter():
        # Check if the element is <w> or <pc>
        if elem.tag in [f'{{{namespaces["ns"]}}}w', f'{{{namespaces["ns"]}}}pc']:
            if elem.get('synch'):
                word_synch = elem.attrib["synch"]
                word_start = next((num for str_, num in time_list if str_ == word_synch[1:]), None)
                word_end = next((time_list[i+1][1] for i in range(len(time_list)-1) if time_list[i][0] == word_synch[1:]), None)
            else:
                word_start = None
                word_end = None
            if elem.text:
                word_intervals.append((word_start, word_end, elem.text))
   
    # Remove intervals containing only punctuation
    word_intervals = [t for t in word_intervals if t[-1] not in string.punctuation]
    # Remove intervals containing only ellipsis
    word_intervals = [t for t in word_intervals if t[-1] != '…']
    #Remove words containing only escape sequences
    word_intervals = [t for t in word_intervals if not re.match(r'^[\s\r\n\t]*$', t[-1])]

    return word_intervals

def extract_FA_intervals(fa_filepath):

    if fa_filepath.endswith(".TextGrid"):
        tg = TextGrid.fromFile(fa_filepath)
        word_intervals = tg.getFirst("strd-wrd-sgmnt")
        word_intervals = [(interval.minTime, interval.maxTime, interval.mark) for interval in word_intervals] 

    elif fa_filepath.endswith(".ctm"):
        df = pd.read_csv(fa_filepath, delimiter=' ', header=None, quoting=csv.QUOTE_NONE)
        word_intervals = df.iloc[:,2:5]
        word_intervals = list(word_intervals.itertuples(index=False, name=None))

    # Remove empty or whitespace-only word intervals
    word_intervals = [interval for interval in word_intervals if interval[-1].strip()]
    # Remove anonymized words
    word_intervals = [interval for interval in word_intervals if not ('[' in interval[-1] and ']' in interval[-1])]
    # Remove intervals containing only punctuation
    word_intervals = [t for t in word_intervals if t[-1].replace('"', '') not in string.punctuation]
    # Remove intervals containing only ellipsis
    word_intervals = [t for t in word_intervals if t[-1] != '…']
    word_intervals = [t for t in word_intervals if t[-1] != '...']
    #Remove words containing only escape sequences
    word_intervals = [t for t in word_intervals if not re.match(r'^[\s\r\n\t]*$', t[-1])]

    return word_intervals

def calculate_tolerance_ratio(differences, tolerance):
    # Calculate the ratio of files within a specific tolerance
    within_tolerance = [diff <= tolerance for diff in differences]
    ratio = sum(within_tolerance) / len(within_tolerance)
    return ratio

if __name__ == "__main__":
    # Call examples:
    # python aligner_eval.py "data/Gos.TEI.2.1/Artur-J/*.xml" "data/nemo/output/Artur-J/ctm/words/*.ctm"
    # python aligner_eval.py "data/Gos.TEI.2.1/Artur-N/*.xml" "data/nemo/output/Artur-N/ctm/words/*.ctm"
    # python aligner_eval.py "data/Gos.TEI.2.1/GosVL/*.xml" "data/nemo/output/GosVL/ctm/words/*.ctm"
    # python aligner_eval.py "data/Gos.TEI.2.1/Artur-J/*.xml" "data/gos_processed/Artur-J/TextGrid_final/*.TextGrid"
    # python aligner_eval.py "data/Gos.TEI.2.1/Artur-N/*.xml" "data/gos_processed/Artur-N/TextGrid_final/*.TextGrid"
    # python aligner_eval.py "data/Gos.TEI.2.1/GosVL/*.xml" "data/gos_processed/GosVL/TextGrid_final/*.TextGrid"


    if len(sys.argv) < 3:
        print("Usage: aligner_eval.py <gt_filepath_or_pattern> <fa_filepath_or_pattern>")
        sys.exit(1)

    gt_pattern = sys.argv[1]
    fa_pattern = sys.argv[2]

    # Extracting the directory and file extension for both patterns
    gt_dir, gt_extension = os.path.dirname(gt_pattern), os.path.splitext(gt_pattern)[1]
    fa_dir, fa_extension = os.path.dirname(fa_pattern), os.path.splitext(fa_pattern)[1]

    # Use glob to get a list of GT files
    gt_files = sorted(glob.glob(gt_pattern))
    all_differences = []

    for gt_filepath in gt_files:
        # Construct FA filepath by matching the basename and using the FA extension
        base_name = os.path.basename(gt_filepath).replace(gt_extension, "")
        #fa_filepath = os.path.join(fa_dir, base_name + "-avd" + fa_extension)
        fa_filepath = os.path.join(fa_dir, base_name + fa_extension)

        # Check if the FA file exists
        if not os.path.exists(fa_filepath):
            print(f"Warning: No corresponding FA file found for {gt_filepath}")
            continue

        GT_words = extract_GT_intervals(gt_filepath)
        FA_words = extract_FA_intervals(fa_filepath)
        if len(GT_words) != len(FA_words):
            print(f"Warning: Skipping file {gt_filepath} since the number of GT words is different than FA words ({len(GT_words)} != {len(FA_words)}).")
            continue

        if all(t[0] is None for t in GT_words):
            print(f"Warning: Skipping file {gt_filepath} since it has no GT annotations.")
            continue

        # Aligning and computing the differences as before
        aligned_words = [(t1, t2) for t1, t2 in zip(GT_words, FA_words) if None not in t1]
        GT_words, FA_words = zip(*aligned_words)
        GT_start = np.array([elem[0] for elem in GT_words])
        FA_start = np.array([elem[0] for elem in FA_words])
        differences = np.abs(GT_start - FA_start) * 1000
        # Keep only elements less than the threshold (higher error are attriburted to impresice GT annotations)
        differences = differences[differences < 5000]
        all_differences.append(differences)
        print(f"File {gt_filepath}: Mean difference: {round(np.mean(differences), 2)}, median difference: {round(np.median(differences), 2)}")

        if len(sys.argv) == 4:
            all_data = [(a, x, c) for ((a, _, c), (x, _, _)) in zip(GT_words, FA_words)]
            with open(os.path.join(sys.argv[3], base_name + '.csv'), 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(all_data)

    all_differences = np.hstack(all_differences)
    print(f"Overall mean difference: {round(np.mean(all_differences), 1)}")
    print(f"Overall median difference: {round(np.median(all_differences), 1)}")

    # Calculate percentages for each tolerance
    tolerances = [10, 50, 100]
    for tolerance in tolerances:
        ratio = calculate_tolerance_ratio(all_differences, tolerance)
        print(f"Ratio of boundaries within {tolerance}ms tolerance: {round(ratio, 2)}")

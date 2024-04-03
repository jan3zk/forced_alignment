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
        if elem.tag in [f'{{{namespaces["ns"]}}}w', f'{{{namespaces["ns"]}}}pc']:# and elem.get('synch'):
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
        df = pd.read_csv(fa_filepath,delimiter=' ', header=None)
        word_intervals = df.iloc[:,2:5]
        word_intervals = list(word_intervals.itertuples(index=False, name=None))

    # Remove empty or whitespace-only word intervals
    word_intervals = [interval for interval in word_intervals if interval[-1].strip()]
    # Remove anonymized words
    word_intervals = [interval for interval in word_intervals if not ('[' in interval[-1] and ']' in interval[-1])]

    return word_intervals

if __name__ == "__main__":
    # Call examples:
    # python aligner_eval.py "data/Gos.TEI.2.1/Artur-J/Artur-J-Gvecg-P500002.xml" "data/nemo/output/ctm/words/Artur-J-Gvecg-P500002-avd.ctm"
    # python aligner_eval.py "data/Gos.TEI.2.1/Artur-N/*.xml" "data/gos_processed/Artur-N/TextGrid_final/*.TextGrid"

    if len(sys.argv) != 3:
        print("Usage: aligner_eval.py <gt_filepath_pattern> <fa_filepath_pattern>")
        sys.exit(1)

    gt_pattern = sys.argv[1]
    fa_pattern = sys.argv[2]

    # Extracting the directory and file extension for both patterns
    gt_dir, gt_extension = os.path.dirname(gt_pattern), os.path.splitext(gt_pattern)[1]
    fa_dir, fa_extension = os.path.dirname(fa_pattern), os.path.splitext(fa_pattern)[1]

    # Use glob to get a list of GT files
    gt_files = glob.glob(gt_pattern)
    all_differences = []
    all_data = []

    for gt_filepath in gt_files:
        # Construct FA filepath by matching the basename and using the FA extension
        base_name = os.path.basename(gt_filepath).replace(gt_extension, "")
        fa_filepath = os.path.join(fa_dir, base_name + "-avd" + fa_extension)

        # Check if the FA file exists
        if not os.path.exists(fa_filepath):
            print(f"Warning: No corresponding FA file found for {gt_filepath}")
            continue

        GT_words = extract_GT_intervals(gt_filepath)
        FA_words = extract_FA_intervals(fa_filepath)

        # Aligning and computing the differences as before
        aligned_words = [(t1, t2) for t1, t2 in zip(GT_words, FA_words) if None not in t1]
        GT_words, FA_words = zip(*aligned_words)
        GT_start = np.array([elem[0] for elem in GT_words])
        FA_start = np.array([elem[0] for elem in FA_words])
        mean_difference = np.mean(np.abs(GT_start - FA_start))
        all_differences.append(mean_difference)
        for gt, fa in zip(GT_start, FA_start):
            all_data.append([base_name, gt, fa])

        print(f"File: {gt_filepath} - Mean difference: {mean_difference}")
    
    overall_mean_difference = np.mean(all_differences)
    print(f"Overall mean difference across all files: {overall_mean_difference}")

    # Writing data to a CSV file
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Filename', 'GT_start', 'FA_start'])
        writer.writerows(all_data)
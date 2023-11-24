import sys
import xml.etree.ElementTree as ET
from utils import parse_textgrid, write_textgrid
from collections import OrderedDict
import string

def parse_xml(xml_file_path):
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Define the TEI and XML namespaces
    namespaces = {'ns': 'http://www.tei-c.org/ns/1.0'}
    xml_ns = 'http://www.w3.org/XML/1998/namespace'

    # Initialize an empty list to store the extracted data
    extracted_data = []

    # Iterate through all elements in the XML file
    for elem in root.iter():
        # Check if the element is <w> or <pc>
        if elem.tag in ['{http://www.tei-c.org/ns/1.0}w', '{http://www.tei-c.org/ns/1.0}pc']:
            word_id = elem.get(f'{{{xml_ns}}}id', 'NoID')
            if elem.text:
                extracted_data.append((word_id, elem.text))

    return extracted_data

def word_id_intervals(tiers, word_ids):
    words = [t[1] for t in word_ids]
    ids = [t[0] for t in word_ids]

    # Assume 'strd-wrd-sgmnt' tier contains word intervals
    strd_wrd_sgmnt = tiers.get('strd-wrd-sgmnt', [])

    # Remove empty or whitespace-only word intervals
    strd_wrd_sgmnt = [interval for interval in strd_wrd_sgmnt if interval[2].strip()]

    # Concatenate the tuples from strd_wrd_sgmnt when they are part of the same word in words
    concatenated_intervals = []
    interval_index = 0

    for word in words:
        dash_count = word.count('-') # Count dashes
        intervals_to_concatenate = 1 + dash_count

        # Start with the initial interval
        start_time, end_time, combined_word = strd_wrd_sgmnt[interval_index]
        interval_index += 1

        # Concatenate additional intervals
        for _ in range(dash_count):
            end_time = strd_wrd_sgmnt[interval_index][1]
            combined_word += strd_wrd_sgmnt[interval_index][2]
            interval_index += 1

        concatenated_intervals.append((start_time, end_time, combined_word))

    # Ensure word count matches
    if len(ids) != len(concatenated_intervals):
        raise ValueError("Word count in transcription and TextGrid do not match.")
    
    # Associate transcription words with their respective intervals
    wordid_intervals = [
        (interval[0], interval[1], ident) 
        for interval, ident in zip(concatenated_intervals, ids)
    ]
    
    return wordid_intervals

def main(input_textgrid, input_xml, output_textgrid):
    # Parse XML to get speaker intervals
    word_ids = parse_xml(input_xml)
    word_ids = [t for t in word_ids if t[1][-1] not in string.punctuation]

    # Load and parse the TextGrid file
    tiers = parse_textgrid(input_textgrid)
    
    # Get time intervals for each word-ID
    word_ids = word_id_intervals(tiers, word_ids)

    # Add the new 'word-ID' tier after the 'strd-wrd-sgmnt' tier in the TextGrid
    extended_tiers = OrderedDict()
    for tier_name, tier_data in tiers.items():
        extended_tiers[tier_name] = tier_data
        if tier_name == 'conversational-trs':
            extended_tiers['word-ID'] = word_ids

    # Write the modified TextGrid content to a new file
    write_textgrid(output_textgrid, extended_tiers)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_word-ID_tier.py [input.TextGrid] [input.xml] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
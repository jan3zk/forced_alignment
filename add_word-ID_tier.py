import sys
import xml.etree.ElementTree as ET
from textgrid import TextGrid, IntervalTier, Interval
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

def word_id_intervals(strd_wrd_sgmnt, word_ids):
    words = [t[1] for t in word_ids]
    ids = [t[0] for t in word_ids]

    # Remove empty or whitespace-only word intervals
    strd_wrd_sgmnt = [interval for interval in strd_wrd_sgmnt if interval[2].strip()]

    # Remove intervals with square brackets (annonimized names that lack word-IDs)
    strd_wrd_sgmnt = [t for t in strd_wrd_sgmnt if '[' not in t[-1] and ']' not in t[-1]]

    if len(words) == len(strd_wrd_sgmnt):
        concatenated_intervals = strd_wrd_sgmnt
    else:
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
        words_fa = [t[-1] for t in concatenated_intervals]
        print("\n".join(f"{a} {b}" for a, b in zip(words, words_fa)))
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
    # Remove intervals containing only punctuation
    word_ids = [t for t in word_ids if t[1][-1] not in string.punctuation]
    # Remove intervals containing only ellipsis
    word_ids = [t for t in word_ids if t[-1] != '…']

    # Load and parse the TextGrid file
    #tiers = parse_textgrid(input_textgrid)

    # Load the input TextGrid
    tg = TextGrid.fromFile(input_textgrid)

    strd_wrd_sgmnt = tg.getFirst("strd-wrd-sgmnt")
    strd_wrd_sgmnt = [(interval.minTime, interval.maxTime, interval.mark) for interval in strd_wrd_sgmnt] 
    
    # Get time intervals for each word-ID
    word_ids = word_id_intervals(strd_wrd_sgmnt, word_ids)

    # Add new tier
    new_tier = IntervalTier(name="word-ID", minTime=min(t[0] for t in word_ids), maxTime=max(t[1] for t in word_ids))
    for start, end, label in word_ids:
        new_tier.addInterval(Interval(start, end, label))
    index = next((i for i, tier in enumerate(tg.tiers) if tier.name=="conversational-trs"), None)
    tg.tiers.insert(index + 1, new_tier)
    
    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_word-ID_tier.py [input.TextGrid] [input.xml] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
import sys
import xml.etree.ElementTree as ET
from utils import parse_textgrid, write_textgrid
from collections import OrderedDict

def extract_transcription(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Assuming the transcription text is within 'Turn' elements
        transcription = ''
        for turn in root.iter('Turn'):
            for sync in turn:
                if sync.tail:
                    transcription += sync.tail.strip() + ' '

        return transcription.strip()
    except Exception as e:
        return f"Error: {e}"

def clean_string(s):
    # Remove special characters and convert to lower case for comparison
    return s.lower().replace('@', '').replace('-', '')

def is_more_similar(combined, current, target):
    # Check if the combined string is more similar to the target word than the current string
    return len(clean_string(combined)) > len(clean_string(current)) and clean_string(target).startswith(clean_string(combined))

def align_transcription_to_words(tiers, transcription):
    # Tokenize the transcription into words
    words = transcription.split()
    
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
    if len(words) != len(concatenated_intervals):
        raise ValueError("Word count in transcription and TextGrid do not match.")
    
    # Associate transcription words with their respective intervals
    transcription_intervals = [
        (interval[0], interval[1], word) 
        for interval, word in zip(concatenated_intervals, words)
    ]
    
    return transcription_intervals

def main(input_trs, input_textgrid, output_textgrid):
    # Load transcription
    transcription = extract_transcription(input_trs)

    # Load and parse the TextGrid file
    tiers = parse_textgrid(input_textgrid)

    aligned_transcription = align_transcription_to_words(tiers, transcription)

    # Add the new tier after the 'speaker-ID' tier in the TextGrid
    extended_tiers = OrderedDict()
    for tier_name, tier_data in tiers.items():
        extended_tiers[tier_name] = tier_data
        if tier_name == 'conversational-trs':
            extended_tiers['cnvrstl-wrd-sgmnt'] = aligned_transcription

    # Save the modified TextGrid
    write_textgrid(output_textgrid, extended_tiers)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_cnvrstl-wrd-sgmnt_tier.py [cnv-transcription.txt] [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
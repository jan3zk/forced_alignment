import sys
import re
import xml.etree.ElementTree as ET
from utils import parse_textgrid, write_textgrid
from collections import OrderedDict
import string

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

def align_pog_transcription_to_words(tiers, transcription):
    # Treat words inside brackets as single word
    transcription = re.sub(r'\[([^]]+)\]', lambda match: "[" + match.group(1).replace(" ", "_") + "]", transcription) 
    
    # Remove ellipsis
    transcription = transcription.replace('...', '')

    # Tokenize the transcription into words
    words = transcription.split()
    
    # Remove empty elements and elements containing only punctuation
    words = [s for s in words if s and not all(char in string.punctuation for char in s)]
    # Remove elements containing only specific symbols
    words = [s for s in words if not (s in ['-', '+', '–'])]

    # Assume 'strd-wrd-sgmnt' tier contains word intervals
    strd_wrd_sgmnt = tiers.get('strd-wrd-sgmnt', [])

    # Remove empty or whitespace-only word intervals
    strd_wrd_sgmnt = [interval for interval in strd_wrd_sgmnt if interval[2].strip()]

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
    if len(words) != len(concatenated_intervals):
        words_fa = [t[-1] for t in concatenated_intervals]
        print("\n".join(f"{a} {b}" for a, b in zip(words, words_fa)))
        raise ValueError("Word count in transcription and TextGrid do not match.")
    
    # Associate pog transcription words with the strd-wrd-sgmnt intervals
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

    aligned_transcription = align_pog_transcription_to_words(tiers, transcription)

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
        print("Usage: python add_cnvrstl-wrd-sgmnt_tier.py [cnv-transcription.trs] [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
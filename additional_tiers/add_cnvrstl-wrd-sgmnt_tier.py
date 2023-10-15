import sys
from utils import parse_textgrid, write_textgrid
from collections import OrderedDict


def align_transcription_to_words(tiers, transcription):
    # Tokenize the transcription into words
    words = transcription.split()
    
    # Assume 'word_intervals' tier contains word intervals
    word_intervals = tiers.get('strd-wrd-sgmnt', [])

    # Remove empty or whitespace-only word intervals
    word_intervals = [interval for interval in word_intervals if interval[2].strip()]

    # Ensure word count matches
    if len(words) != len(word_intervals):
        raise ValueError("Word count in transcription and TextGrid do not match.")
    
    # Associate transcription words with their respective intervals
    transcription_intervals = [
        (interval[0], interval[1], word) 
        for interval, word in zip(word_intervals, words)
    ]
    
    return transcription_intervals


def main(input_trs, input_textgrid, output_textgrid):
    # Load transcription
    with open(input_trs) as f:
        transcription = f.read()

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
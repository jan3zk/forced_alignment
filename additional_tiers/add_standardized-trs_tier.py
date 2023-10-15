import sys
from utils import parse_textgrid, write_textgrid
from collections import OrderedDict


def align_transcription_to_speaker(tiers, transcription):
    # Tokenize the transcription into words
    words = transcription.split()
    
    # Assume 'word_intervals' tier contains word intervals
    word_intervals = tiers.get('strd-wrd-sgmnt', [])
    speaker_intervals = tiers.get('speaker-ID', [])

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
    
    # Placeholder for aligned transcription segments
    aligned_transcription = []

    # Logic for assigning each word to a speaker
    for speaker_interval in speaker_intervals:
        speaker_start, speaker_end, speaker_label = speaker_interval

        # Concatenate words falling into the speaker interval
        # More than half of the word's duration should fall within the speaker interval.
        words_in_speaker_interval = [
            word for start, end, word in transcription_intervals
            if max(0, min(end, speaker_end) - max(start, speaker_start)) >= 0.5 * (end - start)
        ]
        concatenated_words = ' '.join(words_in_speaker_interval)
        
        # Add to aligned transcription
        aligned_transcription.append((speaker_start, speaker_end, concatenated_words))

    # Return aligned_transcription
    return aligned_transcription


def main(input_trs, input_textgrid, output_textgrid):
    # Load transcription
    with open(input_trs) as f:
        transcription = f.read()

    # Load and parse the TextGrid file
    tiers = parse_textgrid(input_textgrid)

    aligned_transcription = align_transcription_to_speaker(tiers, transcription)

    # Add the new tier after the 'speaker-ID' tier in the TextGrid
    extended_tiers = OrderedDict()
    for tier_name, tier_data in tiers.items():
        extended_tiers[tier_name] = tier_data
        if tier_name == 'speaker-ID':
            extended_tiers['standardized-trs'] = aligned_transcription

    # Save the modified TextGrid
    write_textgrid(output_textgrid, extended_tiers)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_standardized-trs_tier.py [std-transcription.txt] [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
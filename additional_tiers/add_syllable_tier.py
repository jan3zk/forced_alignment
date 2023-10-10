import re
import sys
import slovene_syllable_splitter as syllable_splitter
import slovene_phoneme_syllable_splitter as syllable_phoneme_splitter
from collections import OrderedDict
from utils import parse_textgrid, write_textgrid


def create_syllable_tier(phoneme_intervals, word_intervals):
    """
    Create a syllable tier based on phoneme intervals using the slovene_phoneme_syllable_splitter for time intervals 
    and slovene_syllable_splitter for syllable labels.
    
    Parameters:
    - phoneme_intervals: List of tuples containing phoneme intervals (start, end, label).
    - word_intervals: List of tuples containing word intervals (start, end, label).
    
    Returns:
    - syllable_intervals: List of tuples containing syllable intervals (start, end, label).
    """
    syllable_intervals = []
    vowel_graphemes = syllable_splitter.get_vowel_graphemes()
    
    # Index to keep track of the current phoneme
    phoneme_idx = 0
    
    # Processing each word interval
    for word_start, word_end, word_label in word_intervals:
        # Extracting phoneme intervals corresponding to the current word
        word_phoneme_intervals = []
        while (
            phoneme_idx < len(phoneme_intervals) and 
            phoneme_intervals[phoneme_idx][1] <= word_end
        ):
            if phoneme_intervals[phoneme_idx][0] >= word_start:
                word_phoneme_intervals.append(phoneme_intervals[phoneme_idx])
            phoneme_idx += 1
        
        # Getting grapheme-based syllables using slovene_syllable_splitter
        grapheme_syllables = syllable_splitter.create_syllables(word_label, vowel_graphemes)
        
        # Converting phoneme labels of the word into a single string
        phoneme_labels_str = ' '.join([label for _, _, label in word_phoneme_intervals])
        
        # Getting phoneme-based syllables using slovene_phoneme_syllable_splitter
        phoneme_syllables = syllable_phoneme_splitter.syllabize_phonemes(phoneme_labels_str)
        
        if grapheme_syllables:
            if len(grapheme_syllables) == len(phoneme_syllables):
                # Creating syllable intervals based on identified syllables within the word
                word_phoneme_idx = 0
                for grapheme_syllable, phoneme_syllable in zip(grapheme_syllables, phoneme_syllables):
                    syllable_phoneme_count = len(phoneme_syllable.split())
                    start_time = word_phoneme_intervals[word_phoneme_idx][0]
                    end_time = word_phoneme_intervals[word_phoneme_idx + syllable_phoneme_count - 1][1]
                    syllable_intervals.append((start_time, end_time, grapheme_syllable.replace(" ", "")))
                    word_phoneme_idx += syllable_phoneme_count
            else:
                # If there's a mismatch, divide the word interval equally among grapheme syllables
                syllable_duration = (word_end - word_start) / len(grapheme_syllables)
                for i, grapheme_syllable in enumerate(grapheme_syllables):
                    start_time = word_start + i * syllable_duration
                    end_time = start_time + syllable_duration
                    syllable_intervals.append((start_time, end_time, grapheme_syllable.replace(" ", "")))
    
    return syllable_intervals

def main(input_textgrid_path, output_textgrid_path):
    # Read the TextGrid file content
    with open(input_textgrid_path, 'r') as f:
        textgrid_content = f.read()
    
    # Parse the TextGrid file to extract phoneme and word intervals
    parsed_textgrid = parse_textgrid(textgrid_content)
    phoneme_intervals = parsed_textgrid['phones']
    word_intervals = parsed_textgrid['words']
    
    # Split phonemes into syllables and identify their intervals
    syllable_intervals = create_syllable_tier(phoneme_intervals, word_intervals)
    
    # Write the extended TextGrid file
    extended_tiers = OrderedDict([
        ('words', word_intervals),
        ('syllables', syllable_intervals),
        ('phones', phoneme_intervals)
    ])
    write_textgrid(output_textgrid_path, extended_tiers)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_syllable_tier.py [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2])
import sys
import slovene_phoneme_syllable_splitter as syllable_phoneme_splitter
from collections import OrderedDict
from utils import parse_textgrid, write_textgrid


def concatenate_single_letter_syllables(syllable_intervals):
    """
    Concatenate single-letter syllables with the next syllable and adjust time intervals accordingly.

    Parameters:
    - syllable_intervals: List of tuples containing syllable intervals (start, end, label).

    Returns:
    - concatenated_syllable_intervals: List of tuples with concatenated syllables and intervals.
    """
    single_letter_syllables = ['s', 'z', 'h', 'x', 'k', 'v', 'w', 'W']
    concatenated_syllable_intervals = []
    skip_next = False
    
    for i in range(len(syllable_intervals)):
        if skip_next:
            skip_next = False
            continue
        
        start, end, label = syllable_intervals[i]
        
        if label in single_letter_syllables and i < len(syllable_intervals) - 1:
            next_start, next_end, next_label = syllable_intervals[i+1]
            concatenated_label = label + next_label
            concatenated_interval = (start, next_end, concatenated_label)
            concatenated_syllable_intervals.append(concatenated_interval)
            skip_next = True  # Skip the next iteration since we've concatenated it
        else:
            concatenated_syllable_intervals.append((start, end, label))

    return concatenated_syllable_intervals

def create_syllable_tier(phoneme_intervals, word_intervals):
    """
    Create a syllable tier based on phoneme intervals using the slovene_phoneme_syllable_splitter.

    Parameters:
    - phoneme_intervals: List of tuples containing phoneme intervals (start, end, label).
    - word_intervals: List of tuples containing word intervals (start, end, label).

    Returns:
    - syllable_intervals: List of tuples containing syllable intervals (start, end, label).
    """
    syllable_intervals = []

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

        # Converting phoneme labels of the word into a single string
        phoneme_labels_str = ' '.join([label for _, _, label in word_phoneme_intervals])

        # Getting phoneme-based syllables using slovene_phoneme_syllable_splitter
        phoneme_syllables = syllable_phoneme_splitter.syllabize_phonemes(phoneme_labels_str)

        if phoneme_syllables[0]:
            # Creating syllable intervals based on identified syllables within the word
            word_phoneme_idx = 0
            for phoneme_syllable in phoneme_syllables:
                syllable_phoneme_count = len(phoneme_syllable.split())
                start_time = word_phoneme_intervals[word_phoneme_idx][0]
                end_time = word_phoneme_intervals[word_phoneme_idx + syllable_phoneme_count - 1][1]
                syllable_intervals.append((start_time, end_time, phoneme_syllable.replace(" ", "")))
                word_phoneme_idx += syllable_phoneme_count

    return syllable_intervals

def main(input_textgrid, output_textgrid):
    # Parse the TextGrid file to extract phoneme and word intervals
    parsed_textgrid = parse_textgrid(input_textgrid)
    phoneme_intervals = parsed_textgrid['phones']
    word_intervals = parsed_textgrid['words']

    # Split phonemes into syllables and identify their intervals
    syllable_intervals = create_syllable_tier(phoneme_intervals, word_intervals)
    
    # Concatenate single-letter syllables and their intervals
    concatenated_syllable_intervals = concatenate_single_letter_syllables(syllable_intervals)
    
    # Write the extended TextGrid file
    extended_tiers = OrderedDict([
        ('words', word_intervals),
        ('syllables', concatenated_syllable_intervals),
        ('phones', phoneme_intervals)
    ])
    write_textgrid(output_textgrid, extended_tiers)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_syllable_tier.py [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2])

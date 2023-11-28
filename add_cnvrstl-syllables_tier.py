import sys
import re
import string
import slovene_phoneme_syllable_splitter as syllable_phoneme_splitter
from textgrid import TextGrid, IntervalTier, Interval
from utils import extract_transcription

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

def align_std_transcription_to_words(strd_wrd_sgmnt, transcription):
    # Treat words inside brackets as single word
    transcription = re.sub(r'\[([^]]+)\]', lambda match: "[" + match.group(1).replace(" ", "_") + "]", transcription) 
    # Remove ellipsis
    transcription = transcription.replace('...', '')
    # Take care of quotes
    transcription = transcription.replace('"', '""')

    # Tokenize the transcription into words
    words = transcription.split()
    
    # Remove empty elements and elements containing only punctuation
    words = [s for s in words if s and not all(char in string.punctuation for char in s)]
    # Remove elements containing only '–', '+', '-'
    words = [s for s in words if not (s in ['-', '+', '–'])]

    # Remove empty or whitespace-only word intervals
    strd_wrd_sgmnt = [interval for interval in strd_wrd_sgmnt if interval[2].strip()]

    if len(words) == len(strd_wrd_sgmnt):
        concatenated_intervals = strd_wrd_sgmnt
    else:
        # Concatenate the tuples from strd_wrd_sgmnt when they are part of the same word in words
        concatenated_intervals = []
        interval_index = 0
        for word in words:
            dash_count = sum(1 for i in range(len(word) - 1) if word[i] == '-' and not word[i + 1] in '.,;:!?') + (word[-1] == '-')
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

def main(input_textgrid, input_trs, output_textgrid):
    # Load the TextGrid file
    tg = TextGrid.fromFile(input_textgrid)

    # Extract phoneme and word intervals directly from the TextGrid object
    phoneme_intervals = [(interval.minTime, interval.maxTime, interval.mark) for interval in tg.getFirst("phones").intervals]
    word_intervals = [(interval.minTime, interval.maxTime, interval.mark) for interval in tg.getFirst("words").intervals]

    # Split phonemes into syllables and identify their intervals
    syllable_intervals = create_syllable_tier(phoneme_intervals, word_intervals)
        
    # Concatenate single-letter syllables and their intervals
    concatenated_syllable_intervals = concatenate_single_letter_syllables(syllable_intervals)
        
    # Load transcription
    std_transcription = extract_transcription(input_trs)
    
    # Align std words to the intervals returned by forced alignment
    aligned_transcription = align_std_transcription_to_words(word_intervals, std_transcription)

    # Create new IntervalTiers for the extended tiers
    strd_wrd_sgmnt_tier = IntervalTier(name="strd-wrd-sgmnt", minTime=tg.getFirst('words')[0].minTime, maxTime=tg.getFirst('words')[-1].maxTime)
    for start, end, label in aligned_transcription:
        strd_wrd_sgmnt_tier.addInterval(Interval(start, end, label))
    cnvrstl_syllables_tier = IntervalTier(name="cnvrstl-syllables", minTime=tg.getFirst('words')[0].minTime, maxTime=tg.getFirst('words')[-1].maxTime)
    for start, end, label in concatenated_syllable_intervals:
        cnvrstl_syllables_tier.addInterval(Interval(start, end, label))
    phones_tier = IntervalTier(name="phones", minTime=tg.getFirst('words')[0].minTime, maxTime=tg.getFirst('words')[-1].maxTime)
    for start, end, label in phoneme_intervals:  # Assuming phoneme_intervals is defined and populated earlier
        phones_tier.addInterval(Interval(start, end, label))

    # Create a new TextGrid and add the tiers
    new_tg = TextGrid(minTime=tg.minTime, maxTime=tg.maxTime)
    new_tg.append(strd_wrd_sgmnt_tier)
    new_tg.append(cnvrstl_syllables_tier)
    new_tg.append(phones_tier)

    # Save the new TextGrid
    new_tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_cnvrstl-syllables_tier.py [input.TextGrid] [input.trs] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])

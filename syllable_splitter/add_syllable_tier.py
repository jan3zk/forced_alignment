import re
import sys
import slovene_syllable_splitter as syllable_splitter
import slovene_phoneme_syllable_splitter as syllable_phoneme_splitter
from collections import OrderedDict


def parse_textgrid(textgrid_content):
    """
    Parse the content of a TextGrid file and extract relevant information.
    Returns a dictionary with tiers, each containing intervals with start time, end time, and label.
    """
    # Extracting tiers using regex
    tier_pattern = re.compile(r'item \[\d+\]:\s*class = "IntervalTier"\s*name = "(.*?)"\s*xmin = [\d.]+\s*xmax = [\d.]+\s*intervals: size = \d+\s*((?:\s*intervals \[\d+\]:\s*xmin = [\d.]+\s*xmax = [\d.]+\s*text = ".*?"\s*)*)', re.DOTALL)
    interval_pattern = re.compile(r'intervals \[\d+\]:\s*xmin = ([\d.]+)\s*xmax = ([\d.]+)\s*text = "(.*?)"\s*', re.DOTALL)
    
    tiers = {}
    for tier_match in tier_pattern.finditer(textgrid_content):
        tier_name = tier_match.group(1)
        tier_intervals_str = tier_match.group(2)
        
        # Extracting intervals from the tier
        intervals = []
        for interval_match in interval_pattern.finditer(tier_intervals_str):
            xmin, xmax, text = interval_match.groups()
            intervals.append((float(xmin), float(xmax), text))
        
        tiers[tier_name] = intervals
    
    return tiers

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
        
        # Using syllabize_phonemes to identify syllables within the word for time intervals
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

def map_syllable_labels(word_intervals, syllable_intervals, grapheme_syllables):
    """
    Map phoneme-based syllable labels with grapheme-based labels using word intervals and grapheme syllables.

    Parameters:
    - word_intervals: List of tuples containing word intervals (start, end, label).
    - syllable_intervals: List of tuples containing syllable intervals (start, end, label).
    - grapheme_syllables: List of lists containing grapheme-based syllables for each word.
    
    Returns:
    - mapped_syllable_intervals: List of tuples containing syllable intervals (start, end, label) with mapped labels.
    """
    mapped_syllable_intervals = []
    syllable_idx = 0

    # Iterate through word intervals and grapheme syllables simultaneously
    for (word_start, word_end, _), word_syllables in zip(word_intervals, grapheme_syllables):
        # Find the corresponding syllable intervals for the current word
        while syllable_idx < len(syllable_intervals) and syllable_intervals[syllable_idx][1] <= word_end:
            # If the syllable interval falls within the word interval, replace the label
            if syllable_intervals[syllable_idx][0] >= word_start:
                # Extracting start and end times of the syllable interval
                syllable_start, syllable_end, _ = syllable_intervals[syllable_idx]
                
                # Check for syllable availability and mapping the label
                if word_syllables:
                    syllable_label = word_syllables.pop(0)
                    mapped_syllable_intervals.append((syllable_start, syllable_end, syllable_label))
                else:
                    # If no syllables are available, add an empty label interval
                    mapped_syllable_intervals.append((syllable_start, syllable_end, ""))
            
            # Move to the next syllable interval
            syllable_idx += 1
    
    return mapped_syllable_intervals

def write_textgrid(file_path, tiers):
    """
    Write a TextGrid file given a set of tiers.

    Parameters:
    - file_path: String specifying the path to save the TextGrid file.
    - tiers: Dictionary containing tier names and their respective intervals.

    Returns:
    - None
    """
    with open(file_path, 'w') as f:
        # Writing file header
        f.write('File type = "ooTextFile"\n')
        f.write('Object class = "TextGrid"\n')
        f.write('\n')
        f.write('xmin = 0\n')
        f.write(f'xmax = {max(interval[1] for intervals in tiers.values() for interval in intervals)}\n')
        f.write('tiers? <exists>\n')
        f.write(f'size = {len(tiers)}\n')
        f.write('item []:\n')
        
        # Writing each tier
        for i, (tier_name, intervals) in enumerate(tiers.items(), start=1):
            f.write(f'    item [{i}]:\n')
            f.write('        class = "IntervalTier"\n')
            f.write(f'        name = "{tier_name}"\n')
            f.write('        xmin = 0\n')
            f.write(f'        xmax = {max(end for _, end, _ in intervals)}\n')
            f.write(f'        intervals: size = {len(intervals)}\n')
            
            # Writing each interval
            for j, (start, end, label) in enumerate(intervals, start=1):
                f.write(f'        intervals [{j}]:\n')
                f.write(f'            xmin = {start}\n')
                f.write(f'            xmax = {end}\n')
                f.write(f'            text = "{label}"\n')

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
    # Example usage: python add_syllable_tier.py input.TextGrid output.TextGrid
    input_textgrid_path = sys.argv[1]
    output_textgrid_path = sys.argv[2]
    main(input_textgrid_path, output_textgrid_path)

import sys
import re
from textgrid import TextGrid, IntervalTier, Interval
from utils import extract_transcription
import string

def align_pog_transcription_to_words(strd_wrd_sgmnt, transcription):
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
    pog_intervals = [
        (interval[0], interval[1], word) 
        for interval, word in zip(concatenated_intervals, words)
    ]
    
    return pog_intervals

def main(input_trs, input_textgrid, output_textgrid):
    # Load transcription
    transcription = extract_transcription(input_trs)

    # Load the input TextGrid
    tg = TextGrid.fromFile(input_textgrid)

    strd_wrd_sgmnt = tg.getFirst("strd-wrd-sgmnt")
    strd_wrd_sgmnt = [(interval.minTime, interval.maxTime, interval.mark) for interval in strd_wrd_sgmnt]
    pog_trs = align_pog_transcription_to_words(strd_wrd_sgmnt, transcription)

    # Add new tier
    new_tier = IntervalTier(name="cnvrstl-wrd-sgmnt", minTime=min(t[0] for t in pog_trs), maxTime=max(t[1] for t in pog_trs))
    for start, end, label in pog_trs:
        new_tier.addInterval(Interval(start, end, label))
    index = next((i for i, tier in enumerate(tg.tiers) if tier.name=="conversational-trs"), None)
    tg.tiers.insert(index + 1, new_tier)

    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_cnvrstl-wrd-sgmnt_tier.py [cnv-transcription.trs] [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
import re
import string

def align_transcription_to_words(strd_wrd_sgmnt, transcription):
    # Treat words inside the brackets as single word
    transcription = re.sub(r'\[([^]]+)\]', lambda match: "[" + match.group(1).replace(" ", "_") + "]", transcription) 

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
        for i, word in enumerate(words):
            # Start with the initial interval
            if interval_index >= len(strd_wrd_sgmnt):
                break
            start_time, end_time, combined_word = strd_wrd_sgmnt[interval_index]
            interval_index += 1
            dash_count_word = sum(1 for i in range(1,len(word) - 1) if word[i] in ['-','&'] and not word[i + 1] in '.,;:!?')
            dash_count_sgmnt = sum(1 for i in range(1,len(combined_word) - 1) if combined_word[i] in ['-','&'] and not combined_word[i + 1] in '.,;:!?')
            dash_count = dash_count_word - dash_count_sgmnt
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
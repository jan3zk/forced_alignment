import sys
from textgrid import TextGrid, IntervalTier, Interval
import string

def load_discourse_markers(file_path):
    with open(file_path, 'r') as file:
        markers = file.read().splitlines()
    
    # Either include or exclude makrers that start with an asterisk
    markers = [marker.replace('*', '').strip() for marker in markers] # include
    #markers = [marker.strip() for marker in markers if not marker.startswith('*')] # exclude
    
    # Sort markers by length (longest first)
    markers.sort(key=lambda x: len(x), reverse=True)
    return markers

def detect_discourse_markers(word_intervals, single_markers, multi_markers):
    discourse_marker_tier = []
    index = 0
    while index < len(word_intervals):
        start, _, label = word_intervals[index]
        normalized_label = label.strip().lower()

        # Initialize variables for checking multi-word discourse markers
        matched_marker = None
        matched_end = None

        # Check for multi-word discourse markers first
        for marker in multi_markers:
            marker_words = marker.split()
            match_count = 0

            # Check if the following words match the multi-word discourse marker
            for offset, marker_word in enumerate(marker_words):
                if (index + offset) < len(word_intervals) and marker_word == word_intervals[index + offset][2].strip().lower():
                    match_count += 1
                else:
                    break

            # If all words of the marker are found consecutively
            if match_count == len(marker_words):
                matched_marker = marker
                matched_end = word_intervals[index + match_count - 1][1]  # End time of the last word
                break

        # If a multi-word marker is matched, append it
        if matched_marker:
            discourse_marker_tier.append((start, matched_end, 'POS'))
            index += len(matched_marker.split())  # Skip the matched words
        else:
            # Check for single-word discourse markers if no multi-word marker is found
            if normalized_label in single_markers:
                end = word_intervals[index][1]  # End time of the current word
                discourse_marker_tier.append((start, end, 'POS'))
            index += 1  # Move to the next interval

    return discourse_marker_tier

def main(input_textgrid, output_textgrid, marker_file):
    # Load discourse markers from the file
    all_markers = load_discourse_markers(marker_file)
    single_markers = {m for m in all_markers if ' ' not in m}
    multi_markers = {m for m in all_markers if ' ' in m}

    # Load and parse the TextGrid file
    tg = TextGrid.fromFile(input_textgrid)

    strd_wrd_sgmnt = tg.getFirst("strd-wrd-sgmnt")
    strd_wrd_sgmnt = [(interval.minTime, interval.maxTime, interval.mark) for interval in strd_wrd_sgmnt]
    # Remove all punctuation
    strd_wrd_sgmnt = [(t[0], t[1], t[2].translate(str.maketrans('', '', string.punctuation))) for t in strd_wrd_sgmnt]
    dm_intervals = detect_discourse_markers(strd_wrd_sgmnt, single_markers, multi_markers)

    # Add new tier
    new_tier = IntervalTier(name="discourse-marker", minTime=tg.minTime, maxTime=tg.maxTime)
    for start, end, label in dm_intervals:
        new_tier.addInterval(Interval(start, end, label))
    index = next((i for i, tier in enumerate(tg.tiers) if tier.name=="strd-wrd-sgmnt"), None)
    tg.tiers.insert(index + 1, new_tier)

    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_discourse-marker_tier.py [input.TextGrid] [output.TextGrid] [discourse_markers.txt]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])

import sys
from utils import parse_textgrid, write_textgrid
from collections import OrderedDict

def detect_pause(tiers):
    word_intervals = tiers.get('strd-wrd-sgmnt', [])
    
    pause_tier = []
    for start, end, label in word_intervals:
        # Assign 'POS' if the interval text is empty or contains only whitespace, 'NEG' otherwise
        pause_label = 'POS' if not label.strip() else 'NEG'
        pause_tier.append((start, end, pause_label))
    
    return pause_tier


def main(input_textgrid, output_textgrid):
    # Load and parse the TextGrid file
    tiers = parse_textgrid(input_textgrid)

    pause_tier = detect_pause(tiers)

    # Add the new tier to the TextGrid
    tiers['pause'] = pause_tier
    
    # Save the modified TextGrid
    write_textgrid(output_textgrid, tiers)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_pause_tier.py [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2])

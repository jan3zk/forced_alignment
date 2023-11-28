import sys
from textgrid import TextGrid, IntervalTier, Interval

def detect_pause(word_intervals):
    pause_intervals = []
    for start, end, label in word_intervals:
        # Assign 'POS' if the interval text is empty or contains only whitespace, 'NEG' otherwise
        pause_label = 'POS' if not label.strip() else 'NEG'
        pause_intervals.append((start, end, pause_label))
    
    return pause_intervals

def main(input_textgrid, output_textgrid):
    # Load and parse the TextGrid file
    tg = TextGrid.fromFile(input_textgrid)

    strd_wrd_sgmnt = tg.getFirst("strd-wrd-sgmnt")
    strd_wrd_sgmnt = [(interval.minTime, interval.maxTime, interval.mark) for interval in strd_wrd_sgmnt]

    pause_intervals = detect_pause(strd_wrd_sgmnt)

    # Add the new tier to the TextGrid
    new_tier = IntervalTier(name="pause", minTime=min(t[0] for t in pause_intervals), maxTime=max(t[1] for t in pause_intervals))
    for start, end, label in pause_intervals:
        new_tier.addInterval(Interval(start, end, label))
    tg.append(new_tier)

    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_pause_tier.py [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2])

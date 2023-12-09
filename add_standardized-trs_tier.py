import sys
import os
from textgrid import TextGrid, IntervalTier, Interval
from utils_trs import intervals_from_trs
from utils_tei import intervals_from_tei

def main(input_trs, input_textgrid, output_textgrid):
    if os.path.splitext(input_trs)[-1] == ".trs":
        transcription_intervals = intervals_from_trs(input_trs)
    else:
        transcription_intervals = intervals_from_tei(input_trs, True)
    # Remove empty intervals
    transcription_intervals = [t for t in transcription_intervals if t[-1] != '']

    # Load the input TextGrid
    tg = TextGrid.fromFile(input_textgrid)

    # Adjust times to not exceed established limits
    transcription_intervals = [(max(tg.minTime, t[0]), min(tg.maxTime, t[1]), t[2]) for t in transcription_intervals]
    # Remove intervals, where tmin is equal or greater than tmax
    transcription_intervals = [t for t in transcription_intervals if t[0] < t[1]]

    # Add new tier
    new_tier = IntervalTier(name="standardized-trs", minTime=min(t[0] for t in transcription_intervals), maxTime=max(t[1] for t in transcription_intervals))
    for start, end, label in transcription_intervals:
        new_tier.addInterval(Interval(start, end, label))

    index = next((i for i, tier in enumerate(tg.tiers) if tier.name=="speaker-ID"), None)
    tg.tiers.insert(index + 1, new_tier)

    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_standardized-trs_tier.py [input.trs] [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])

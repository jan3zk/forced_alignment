import sys
from textgrid import TextGrid, IntervalTier

def adjust_intervals(textgrid_file, initial_trim_time, output_file):
    # Load the TextGrid file
    tg = TextGrid.fromFile(textgrid_file)

    # Adjust and round the overall xmin and xmax of the TextGrid
    tg.minTime = round(tg.minTime + initial_trim_time, 3)
    tg.maxTime = round(tg.maxTime + initial_trim_time, 3)

    # Iterate through each tier and adjust xmin, xmax and intervals
    for tier in tg.tiers:
        if isinstance(tier, IntervalTier):
            # Adjust and round xmin and xmax for each tier
            tier.minTime = round(tier.minTime + initial_trim_time, 3)
            tier.maxTime = round(tier.maxTime + initial_trim_time, 3)

            # Adjust and round the intervals
            for interval in tier:
                interval.minTime = round(interval.minTime + initial_trim_time, 3)
                interval.maxTime = round(interval.maxTime + initial_trim_time, 3)

    # Write the adjusted TextGrid back to a file
    tg.write(output_file)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python compensate_trimming.py <textgrid_file> <initial_trim_time> <output_file>")
        sys.exit(1)

    textgrid_file = sys.argv[1]
    initial_trim_time = float(sys.argv[2])  # Convert string argument to float
    output_file = sys.argv[3]

    adjust_intervals(textgrid_file, initial_trim_time, output_file)

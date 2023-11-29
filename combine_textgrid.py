import textgrid
import sys
import os
import glob

def combine_textgrid_files(directory, output_file):
    combined_grid = None
    file_paths = glob.glob(os.path.join(directory, '*.TextGrid'))

    for file_path in file_paths:
        tg = textgrid.TextGrid.fromFile(file_path)
        
        if combined_grid is None:
            combined_grid = textgrid.TextGrid()
            for tier in tg.tiers:
                new_tier = textgrid.IntervalTier(name=tier.name)
                combined_grid.append(new_tier)
        
        for i, tier in enumerate(tg.tiers):
            combined_grid[i].intervals.extend(tier.intervals)

    # Sort intervals for each tier and adjust xmin and xmax
    for tier in combined_grid.tiers:
        tier.intervals.sort(key=lambda interval: interval.minTime)
        if tier.intervals:
            tier.minTime = tier.intervals[0].minTime
            tier.maxTime = tier.intervals[-1].maxTime

    # Adjust global xmin and xmax
    combined_grid.minTime = min(tier.minTime for tier in combined_grid.tiers)
    combined_grid.maxTime = max(tier.maxTime for tier in combined_grid.tiers)

    combined_grid.write(output_file)

# Script usage
if len(sys.argv) != 3:
    print("Usage: python script.py <input_directory> <output_file>")
else:
    input_directory = sys.argv[1]
    output_file = sys.argv[2]
    combine_textgrid_files(input_directory, output_file)

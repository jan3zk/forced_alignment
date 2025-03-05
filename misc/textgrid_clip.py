import sys

try:
    import textgrid
except ImportError:
    print("Error: This script requires the 'textgrid' library.")
    print("Please install it with: pip install textgrid")
    sys.exit(1)

def process_textgrid(input_file, output_file, cutoff_time=324.873):
    """
    Process a TextGrid file to:
    - Keep intervals ending before cutoff_time
    - Truncate intervals that cross cutoff_time
    - Discard intervals starting after cutoff_time
    
    Parameters:
    -----------
    input_file : str
        Path to the input TextGrid file
    output_file : str
        Path to the output TextGrid file
    cutoff_time : float
        Timestamp to use as cutoff (default: 324.873)
    """
    # Load the TextGrid file
    tg = textgrid.TextGrid.fromFile(input_file)
    
    # Create a new TextGrid with the same metadata
    new_tg = textgrid.TextGrid(name=tg.name, minTime=tg.minTime, maxTime=min(tg.maxTime, cutoff_time))
    
    # Process each tier in the TextGrid
    for tier in tg:
        # Create a new tier of the same type (IntervalTier or PointTier)
        if isinstance(tier, textgrid.IntervalTier):
            new_tier = textgrid.IntervalTier(name=tier.name, minTime=tier.minTime, maxTime=min(tier.maxTime, cutoff_time))
            
            for interval in tier:
                # Case 1: Interval ends before cutoff - keep as is
                if interval.maxTime <= cutoff_time:
                    new_tier.addInterval(interval)
                # Case 2: Interval starts before cutoff but ends after - truncate
                elif interval.minTime < cutoff_time < interval.maxTime:
                    # Create a modified interval with the same text but ending at cutoff_time
                    modified_interval = textgrid.Interval(
                        interval.minTime, 
                        cutoff_time, 
                        interval.mark
                    )
                    new_tier.addInterval(modified_interval)
                # Case 3: Interval starts after cutoff - discard (do nothing)
        elif isinstance(tier, textgrid.PointTier):
            new_tier = textgrid.PointTier(name=tier.name, minTime=tier.minTime, maxTime=min(tier.maxTime, cutoff_time))
            
            for point in tier:
                # Only keep points before the cutoff time
                if point.time <= cutoff_time:
                    new_tier.addPoint(point)
        
        # Add the new tier to the new TextGrid
        new_tg.append(new_tier)
    
    # Write the modified TextGrid to the output file
    new_tg.write(output_file)
    
    print(f"Processed TextGrid saved to {output_file}")
    print(f"Original TextGrid had {sum(len(tier) for tier in tg)} total intervals/points")
    print(f"Processed TextGrid has {sum(len(tier) for tier in new_tg)} total intervals/points")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_textgrid.py <input_file> <output_file> [cutoff_time]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Allow optional custom cutoff time
    cutoff_time = 324.873
    if len(sys.argv) > 3:
        cutoff_time = float(sys.argv[3])
    
    process_textgrid(input_file, output_file, cutoff_time)
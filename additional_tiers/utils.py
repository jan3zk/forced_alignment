import re


def parse_textgrid(textgrid_path):
    """
    Parse the content of a TextGrid file and extract relevant information.
    Returns a dictionary with tiers, each containing intervals with start time, end time, and label.
    """
    with open(textgrid_path, "r") as file:
        textgrid_content = file.read()

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
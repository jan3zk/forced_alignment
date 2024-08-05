import os
import sys
import glob

def ctm2textgrid(ctm_file, textgrid_file):
    # Converter from NeMo based *.ctm file to Praat *.TextGrid file.
    with open(ctm_file, 'r') as file:
        ctm_lines = file.readlines()
    
    intervals = []
    for line in ctm_lines:
        parts = line.strip().split()
        if len(parts) >= 5:
            start_time = round(float(parts[2]), 2)
            duration = float(parts[3])
            text = parts[4]
            end_time = round(start_time + duration, 2)
            if text != '"':
                intervals.append((start_time, end_time, text))

    if not intervals:
        raise ValueError("No intervals found in CTM file.")

    textgrid_content = [
        'File type = "ooTextFile"',
        'Object class = "TextGrid"',
        '',
        f"xmin = {intervals[0][0]}",
        f"xmax = {intervals[-1][1]}",
        'tiers? <exists>',
        'size = 1',
        'item []:',
        '\titem [1]:',
        '\t\tclass = "IntervalTier"',
        '\t\tname = "strd-wrd-sgmnt"',
        f'\t\txmin = {intervals[0][0]}',
        f'\t\txmax = {intervals[-1][1]}',
        f'\t\tintervals: size = {len(intervals)}',
    ]

    for i, (xmin, xmax, text) in enumerate(intervals, start=1):
        textgrid_content.extend([
            f'\t\t\tintervals [{i}]:',
            f'\t\t\t\txmin = {xmin}',
            f'\t\t\t\txmax = {xmax}',
            f'\t\t\t\ttext = "{text}"',
        ])

    with open(textgrid_file, 'w') as file:
        file.write('\n'.join(textgrid_content))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ctm2textgrid.py <ctm_file_path> <textgrid_output_path>")
        sys.exit(1)

    ctm_file_path = sys.argv[1]
    textgrid_output_path = sys.argv[2]

    ctm_files = glob.glob(ctm_file_path)
    if not ctm_files:
        print(f"No CTM files found for the given path: {ctm_file_path}")
        sys.exit(1)

    for ctm_file in ctm_files:
        base_name = os.path.basename(ctm_file).replace(".ctm", "")
        textgrid_file = os.path.join(textgrid_output_path, base_name + ".TextGrid")
        try:
            ctm2textgrid(ctm_file, textgrid_file)
            print(f"TextGrid created for {ctm_file}")
        except Exception as e:
            print(f"Error processing {ctm_file}: {e}")

import re
import xml.etree.ElementTree as ET

def text_from_trs(trs_file_path):
    try:
        tree = ET.parse(trs_file_path)
        root = tree.getroot()

        # Assuming the transcription text is within 'Turn' elements
        transcription = ''
        for turn in root.iter('Turn'):
            for sync in turn:
                if sync.tail:
                    transcription += sync.tail.strip() + ' '

        return transcription.strip()
    except Exception as e:
        return f"Error: {e}"

def intervals_from_trs(trs_file_path):
    with open(trs_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    intervals = []
    prev_tmin = None  # Initialize prev_tmin to None
    for idx, line in enumerate(lines):
        if not line.startswith('<') and not line.startswith('\n'):
            tmin_match = re.search(r'time="([\d.]+)"', lines[idx - 1], re.IGNORECASE)
            if tmin_match:
                tmin = float(tmin_match.group(1))
                text = line.strip()
                next_idx = idx + 1
                while next_idx < len(lines):
                    next_line = lines[next_idx]
                    if re.search(r'time="([\d.]+)"', next_line, re.IGNORECASE):
                        tmax = float(re.search(r'time="([\d.]+)"', next_line, re.IGNORECASE).group(1))
                        break
                    next_idx += 1
                else:
                    tmax = tmin  # If no next line with "time=" is found, use tmin
                intervals.append((tmin, tmax, text))
                prev_tmin = tmin  # Update prev_tmin only when tmin is successfully parsed
    return intervals

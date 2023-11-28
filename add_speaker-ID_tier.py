import sys
import xml.etree.ElementTree as ET
from textgrid import TextGrid, IntervalTier, Interval

def parse_xml(xml_file_path):
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    # Extract the timeline intervals
    timeline = {}
    for when in root.findall('.//{http://www.tei-c.org/ns/1.0}when'):
        # Extracting xml:id attribute correctly
        xml_id = when.attrib.get('{http://www.w3.org/XML/1998/namespace}id')
        if xml_id:
            interval = float(when.get('interval', '0.0'))
            timeline[xml_id] = interval
    
    # Initialize an empty list to store the extracted speaker intervals
    speaker_intervals = []
    
    # Iterate through all <u> elements in the XML file
    for elem in root.findall('.//{http://www.tei-c.org/ns/1.0}u'):
        start_id = elem.get('start')[1:]  # remove the '#' character
        end_id = elem.get('end')[1:]  # remove the '#' character
        speaker_id = elem.get('who')
    
        # Only process elements with a valid speaker ID
        if speaker_id:
            # Convert start and end ids to actual intervals
            start = timeline.get(start_id, 0.0)
            end = timeline.get(end_id, 0.0)
    
            speaker_intervals.append((start, end, speaker_id))
    
    return speaker_intervals

def merge_overlapping_intervals(intervals):
    # Sort intervals by start time
    intervals.sort(key=lambda x: x[0])

    merged_intervals = []
    current_start, current_end, current_label = intervals[0]

    for next_start, next_end, next_label in intervals[1:]:
        if next_start < current_end:  # Actual overlap, not just adjacent
            # Extend the current interval's end time if necessary
            current_end = max(current_end, next_end)
            # Concatenate labels with a dash
            if next_label not in current_label.split('-'):
                current_label += '-' + next_label
        else:
            # No overlap, add the current interval to the list
            merged_intervals.append((current_start, current_end, current_label))
            # Start a new interval
            current_start, current_end, current_label = next_start, next_end, next_label

    # Add the last interval
    merged_intervals.append((current_start, current_end, current_label))

    return merged_intervals

def main(input_textgrid, input_xml, output_textgrid):
    # Parse XML to get speaker intervals
    xml_speaker_intervals = parse_xml(input_xml)

    # Load and parse the TextGrid file
    tg = TextGrid.fromFile(input_textgrid)

    # Adjust times to not exceed established limits
    xml_speaker_intervals = [(max(tg.minTime, t[0]), min(tg.maxTime, t[1]), t[2]) for t in xml_speaker_intervals]

    # Merge overlapping intervals
    xml_speaker_intervals = merge_overlapping_intervals(xml_speaker_intervals)

    # Create a new interval tier
    new_tier_name = "speaker-ID"

    new_tier = IntervalTier(name=new_tier_name, minTime=min(t[0] for t in xml_speaker_intervals), maxTime=max(t[1] for t in xml_speaker_intervals))
    for start_time, end_time, label in xml_speaker_intervals:
        interval = Interval(minTime=start_time, maxTime=end_time, mark=label)
        new_tier.addInterval(interval)
    tg.tiers.insert(0, new_tier)
    
    # Write the modified TextGrid content to a new file
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_speaker-ID_tier.py [input.TextGrid] [input.xml] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])

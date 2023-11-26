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

        # Convert start and end ids to actual intervals
        start = timeline.get(start_id, 0.0)
        end = timeline.get(end_id, 0.0)

        speaker_intervals.append((start, end, speaker_id))

    return speaker_intervals

def main(input_textgrid, input_xml, output_textgrid):
    # Parse XML to get speaker intervals
    xml_speaker_intervals = parse_xml(input_xml)

    # Load and parse the TextGrid file
    tg = TextGrid.fromFile(input_textgrid)

    # Create a new interval tier
    new_tier_name = "speaker-ID"
    new_tier = IntervalTier(name=new_tier_name)
    for start_time, end_time, label in xml_speaker_intervals:
        interval = Interval(minTime=start_time, maxTime=end_time, mark=label)
        new_tier.addInterval(interval)
    tg.append(new_tier)
    
    # Write the modified TextGrid content to a new file
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_speaker-ID_tier.py [input.TextGrid] [input.xml] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])

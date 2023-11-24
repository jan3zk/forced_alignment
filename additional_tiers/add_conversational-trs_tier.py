import sys
from utils import parse_textgrid, write_textgrid
import xml.etree.ElementTree as ET
from collections import OrderedDict

def parse_trs_file(file_path):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # List to hold the parsed transcription intervals
    transcription_intervals = []

    # Iterate through the XML tree to find 'Turn' elements
    for turn in root.iter('Turn'):
        start_time = float(turn.get('startTime', '0'))
        end_time = float(turn.get('endTime', '0'))

        # Initialize variables for tracking sync times and text
        last_sync_time = start_time
        turn_texts = []

        # Process each element within a 'Turn'
        for element in turn:
            # Check if element is 'Sync', and update last_sync_time accordingly
            if element.tag == 'Sync':
                sync_time = float(element.get('time', '0'))
                if turn_texts:
                    transcription_intervals.append((last_sync_time, sync_time, ' '.join(turn_texts).strip()))
                    turn_texts = []
                last_sync_time = sync_time

            # Append text and tail (if available) to turn_texts
            if element.text:
                turn_texts.append(element.text)
            if element.tail:
                turn_texts.append(element.tail)

        # Append the remaining text after the last sync, if any
        if turn_texts:
            transcription_intervals.append((last_sync_time, end_time, ' '.join(turn_texts).strip()))

    return transcription_intervals

def main(input_trs, input_textgrid, output_textgrid):
    transcription_intervals = parse_trs_file(input_trs)

    # Load and parse the TextGrid file
    tiers = parse_textgrid(input_textgrid)

    # Add the new tier after the 'speaker-ID' tier in the TextGrid
    extended_tiers = OrderedDict()
    for tier_name, tier_data in tiers.items():
        extended_tiers[tier_name] = tier_data
        if tier_name == 'strd-wrd-sgmnt':
            extended_tiers['conversational-trs'] = transcription_intervals

    # Save the modified TextGrid
    write_textgrid(output_textgrid, extended_tiers)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_conversational-trs_tier.py [input.trs] [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])

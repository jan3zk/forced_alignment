import sys
import xml.etree.ElementTree as ET
from textgrid import TextGrid, IntervalTier, Interval
import string
import re
import difflib

def parse_word_id(xml_file_path):
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Define the TEI and XML namespaces
    namespaces = {'ns': 'http://www.tei-c.org/ns/1.0'}
    xml_ns = 'http://www.w3.org/XML/1998/namespace'

    # Initialize an empty list to store the extracted data
    extracted_data = []

    # Iterate through all elements in the XML file
    for elem in root.iter():
        # Check if the element is <w> or <pc>
        if elem.tag in [f'{{{namespaces["ns"]}}}w', f'{{{namespaces["ns"]}}}pc']:
            word_id = elem.get(f'{{{xml_ns}}}id', 'NoID')
            if elem.text:
                extracted_data.append((word_id, elem.text))

    return extracted_data

def word_id_intervals(strd_wrd_sgmnt, word_ids):
    words = [t[1] for t in word_ids]
    ids = [t[0] for t in word_ids]

    # Remove empty or whitespace-only word intervals
    strd_wrd_sgmnt = [interval for interval in strd_wrd_sgmnt if interval[2].strip()]

    # Remove intervals with square brackets (annonimized names that lack word-IDs)
    strd_wrd_sgmnt = [t for t in strd_wrd_sgmnt if '[' not in t[-1] and ']' not in t[-1]]

    fa_words = [interval[2] for interval in strd_wrd_sgmnt]

    matcher = difflib.SequenceMatcher(None, fa_words, words)
    aligned = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in {"equal", "replace"}:
            length = min(i2 - i1, j2 - j1)
            for k in range(length):
                interval = strd_wrd_sgmnt[i1 + k]
                ident = ids[j1 + k]
                aligned.append((interval[0], interval[1], ident))

            if (j2 - j1) > length:
                extra_ids = ids[j1 + length:j2]
                if aligned:
                    s, e, lbl = aligned[-1]
                    aligned[-1] = (s, e, f"{lbl} {' '.join(extra_ids)}")
            elif (i2 - i1) > length:
                for x in range(i1 + length, i2):
                    interval = strd_wrd_sgmnt[x]
                    aligned.append((interval[0], interval[1], fa_words[x]))

        elif tag == "delete":
            for idx in range(i1, i2):
                interval = strd_wrd_sgmnt[idx]
                aligned.append((interval[0], interval[1], fa_words[idx]))

        elif tag == "insert":
            extra_ids = ids[j1:j2]
            if aligned:
                s, e, lbl = aligned[-1]
                aligned[-1] = (s, e, f"{lbl} {' '.join(extra_ids)}")
            else:
                interval = strd_wrd_sgmnt[0]
                aligned.append((interval[0], interval[1], ' '.join(extra_ids)))

    return aligned

def main(input_textgrid, input_xml, output_textgrid):
    # Parse XML to get speaker intervals
    word_ids = parse_word_id(input_xml)
    # Remove intervals containing only punctuation
    word_ids = [t for t in word_ids if t[1] not in string.punctuation]
    # Remove intervals containing only ellipsis
    word_ids = [t for t in word_ids if t[-1] != '…']
    #Remove words containing only escape sequences
    word_ids = [t for t in word_ids if not re.match(r'^[\s\r\n\t]*$', t[1])]
    
    # Load the input TextGrid
    tg = TextGrid.fromFile(input_textgrid)

    strd_wrd_sgmnt = tg.getFirst("strd-wrd-sgmnt")
    strd_wrd_sgmnt = [(interval.minTime, interval.maxTime, interval.mark) for interval in strd_wrd_sgmnt] 
    
    # Get time intervals for each word-ID
    word_ids = word_id_intervals(strd_wrd_sgmnt, word_ids)

    # Add new tier
    new_tier = IntervalTier(name="word-ID", minTime=min(t[0] for t in word_ids), maxTime=max(t[1] for t in word_ids))
    for start, end, label in word_ids:
        new_tier.addInterval(Interval(start, end, label))
    index = next((i for i, tier in enumerate(tg.tiers) if tier.name=="conversational-trs"), None)
    tg.tiers.insert(index + 1, new_tier)
    
    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_word-ID_tier.py [input.TextGrid] [input.xml] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
        
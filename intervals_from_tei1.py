import xml.etree.ElementTree as ET
import sys

def time_lookup_dict(xml_root):
    """
    Creates a dictionary that maps xml:id to interval time for fast lookup.
    Args:
    xml_root (ET.Element): Root element of the parsed XML document.

    Returns:
    dict: A dictionary mapping xml:id to interval time.
    """
    time_dict = {}
    for when_element in xml_root.iterfind('.//{http://www.tei-c.org/ns/1.0}when'):
        xml_id = when_element.attrib.get('{http://www.w3.org/XML/1998/namespace}id')
        interval = float(when_element.attrib.get('interval', 0))
        time_dict[xml_id] = interval
    return time_dict

def word_intervals(xml_file_path, use_norm):
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Define the TEI and XML namespaces
    namespaces = {'ns': 'http://www.tei-c.org/ns/1.0'}
    xml_ns = 'http://www.w3.org/XML/1998/namespace'

    # Create the time lookup dictionary
    time_dict = time_lookup_dict(root)

    # Initialize an empty list to store the extracted data
    word_intrvl = []
    sentence_intrvl = []
    first_word_passed = False
    # Iterate through all elements in the XML file
    for elem in root.iter():
        if elem.get('synch'):
            wtime = time_dict.get(elem.get('synch')[1:])
        else:
            wtime = None
        # Check for the 'gap' element in anonymized words
        if elem.tag == f'{{{namespaces["ns"]}}}gap':
            desc_elem = elem.find('ns:desc', namespaces)
            if desc_elem is not None and desc_elem.text:
                word_intrvl.append((wtime, desc_elem.text))
            continue

        # Check if the element is <w> or <pc>
        if elem.tag in [f'{{{namespaces["ns"]}}}w', f'{{{namespaces["ns"]}}}pc']:
            # Check for the 'norm' attribute
            if elem.text:
                if use_norm:
                    norm_text = elem.get('norm')
                    if norm_text:
                        text = norm_text
                    elif elem.text:
                        text = elem.text
                else:
                    text = elem.text
                word_intrvl.append((wtime, text))

        if first_word_passed and elem.get('synch') and elem.get('synch')[-2:] == "w0":
            sentence = concatenate_words([w[1] for w in word_intrvl[:-1]])
            #sentence_intrvl.append((word_intrvl[0][0], word_intrvl[-1][0], sentence))
            tmax = time_dict.get(".".join(elem.get("synch").split(".")[:2])[1:])
            sentence_intrvl.append((word_intrvl[0][0], tmax, sentence))
            word_intrvl = [word_intrvl[-1]]
        if elem.get('synch') and elem.get('synch')[-2:] == "w0":
            first_word_passed = True
    
    # Add last sentence
    sentence = concatenate_words([w[1] for w in word_intrvl])
    sentence_intrvl.append((word_intrvl[0][0], tmax, sentence))

    return sentence_intrvl

# Function to concatenate the words
def concatenate_words(words):
    sentence = ""
    for word in words:
        if sentence and word not in ",.!?;:":
            sentence += " "
        sentence += word
    return sentence

def main(xml_file_path, use_norm):
    # Extract data
    intervals = word_intervals(xml_file_path, use_norm)
    print(intervals)

if __name__ == '__main__':
    # Set up argument parsing
    if len(sys.argv) < 2:
        print("Usage: python intervals_from_tei.py [xml_file_path] [--use-norm]")
        sys.exit(1)
    xml_file_path = sys.argv[1]
    use_norm = '--use-norm' in sys.argv  # Check if --use-norm flag is present
    main(xml_file_path, use_norm)

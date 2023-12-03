import xml.etree.ElementTree as ET
import sys

def text_from_tei(xml_file_path, use_norm):
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
        # Check for the 'gap' element in anonymized words
        if elem.tag == f'{{{namespaces["ns"]}}}gap':
            desc_elem = elem.find('ns:desc', namespaces)
            if desc_elem is not None and desc_elem.text:
                extracted_data.append(desc_elem.text)
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
                extracted_data.append(text)

    extracted_data = concatenate_words(extracted_data)

    return extracted_data

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

def intervals_from_tei(xml_file_path, use_norm=False):
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
            wname = elem.get('synch')
        else:
            wname = None
        # Check for the 'gap' element in anonymized words
        if elem.tag == f'{{{namespaces["ns"]}}}gap':
            desc_elem = elem.find('ns:desc', namespaces)
            if desc_elem is not None and desc_elem.text:
                word_intrvl.append((wname, desc_elem.text))
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
                word_intrvl.append((wname, text))

        if first_word_passed and elem.get('synch') and elem.get('synch')[-2:] == "w0":
            sentence = concatenate_words([w[1] for w in word_intrvl[:-1]])
            tmin = time_dict.get(".".join(word_intrvl[0][0].split(".")[:2])[1:])
            tmax = time_dict.get(".".join(word_intrvl[-1][0].split(".")[:2])[1:])
            sentence_intrvl.append((tmin, tmax, sentence))
            word_intrvl = [word_intrvl[-1]]
        if elem.get('synch') and elem.get('synch')[-2:] == "w0":
            first_word_passed = True
    
    # Add last sentence
    sentence = concatenate_words([w[1] for w in word_intrvl])
    tmin = time_dict.get(".".join(word_intrvl[0][0].split(".")[:2])[1:])
    tmax = time_dict.get(".".join(increment_last_element_number(word_intrvl[0][0].split(".")[:2]))[1:])
    sentence_intrvl.append((tmin, tmax, sentence))

    return sentence_intrvl

# Function to concatenate the words
def concatenate_words(words):
    sentence = ""
    for word in words:
        if sentence and word not in ",.!?;:":
            sentence += " "
        sentence += word

    return sentence

def increment_last_element_number(lst):
    if not lst:  # Check if the list is empty
        return lst
    last_element = lst[-1]
    # Find the index where the number starts
    for i, char in enumerate(last_element):
        if char.isdigit():
            index = i
            break
    else:  # No numbers found
        return lst
    # Split the string into non-numeric and numeric parts
    non_numeric_part = last_element[:index]
    numeric_part = last_element[index:]
    # Increment the number
    incremented_number = int(numeric_part) + 1
    # Update the last element in the list
    lst[-1] = non_numeric_part + str(incremented_number)

    return lst
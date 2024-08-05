import xml.etree.ElementTree as ET
import sys
import re

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

def timings(xml_root):
    time_list = []
    for when_element in xml_root.iterfind('.//{http://www.tei-c.org/ns/1.0}when'):
        xml_id = when_element.attrib.get('{http://www.w3.org/XML/1998/namespace}id')
        interval = float(when_element.attrib.get('interval', 0))
        time_list.append((xml_id, interval))

    return time_list

def intervals_from_tei(xml_file_path, use_norm=False):
    # This function parses intervals at the sentence level

    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Define the TEI and XML namespaces
    namespaces = {'ns': 'http://www.tei-c.org/ns/1.0'}
    xml_ns = 'http://www.w3.org/XML/1998/namespace'

    # Create the time lookup dictionary
    time_list = timings(root)

    # Initialize an empty list to store the extracted data
    word_intrvl = []
    sentence_intrvl = []
    current_sentence_id = None
    previous_sentence_id = None

    # Iterate through all elements in the XML file
    for elem in root.iter():
        if elem.tag == f'{{{namespaces["ns"]}}}seg':
            previous_sentence_id = current_sentence_id
            current_sentence_id = elem.get('synch')[1:]

        # Check for the 'gap' element in anonymized words
        if elem.tag == f'{{{namespaces["ns"]}}}gap':
            desc_elem = elem.find('ns:desc', namespaces)
            if desc_elem is not None and desc_elem.text:
                word_intrvl.append((current_sentence_id, desc_elem.text))
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
                word_intrvl.append((current_sentence_id, text))

    # Using a dictionary to group and concatenate words inside sentences
    grouped = {}
    for key, value in word_intrvl:
        if key in grouped:
            grouped[key] += " " + value
        else:
            grouped[key] = value

    # Converting the dictionary back into a list of tuples
    sentences = list(grouped.items())
    for sentence in sentences:
        tmin = next((item[1] for item in time_list if item[0] == sentence[0]), None)
        tmax = next((time_list[i+1][1] for i in range(len(time_list)-1) if time_list[i][0] == sentence[0]), None)
        sentence_intrvl.append((tmin, tmax, sentence[1]))

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
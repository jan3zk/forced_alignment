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

    return extracted_data

# Function to concatenate the words
def concatenate_words(words):
    sentence = ""
    for word in words:
        if sentence and word not in ",.!?;:":
            sentence += " "
        sentence += word
    return sentence

def main(xml_file_path, txt_file_path, use_norm):
    # Extract data
    texts = text_from_tei(xml_file_path, use_norm)
    text = concatenate_words(texts)
    
    try:
        with open(txt_file_path, 'w') as file:
            file.write(text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # Set up argument parsing
    if len(sys.argv) < 3:
        print("Usage: python transcript_from_tei.py [input_xml_file_path] [output_txt_file_path] [--use-norm]")
        sys.exit(1)

    xml_file_path = sys.argv[1]
    txt_file_path = sys.argv[2]
    use_norm = '--use-norm' in sys.argv  # Check if --use-norm flag is present

    main(xml_file_path, txt_file_path, use_norm)

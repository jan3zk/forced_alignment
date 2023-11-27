import xml.etree.ElementTree as ET
import argparse
import csv

def extract_text_with_id(xml_file_path):
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
        if elem.tag in ['{http://www.tei-c.org/ns/1.0}w', '{http://www.tei-c.org/ns/1.0}pc']:
            word_id = elem.get(f'{{{xml_ns}}}id', 'NoID')
            if elem.text:
                extracted_data.append((word_id, elem.text))

    return extracted_data

def save_to_csv(data, output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['word_id', 'text'])  # Write headers
        writer.writerows(data)

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Extract text and word IDs from <w> and <pc> tags in an XML file.')
    parser.add_argument('xml_file_path', type=str, help='Path to the XML file')
    parser.add_argument('output_csv', type=str, help='Path to the output CSV file')

    # Parse arguments
    args = parser.parse_args()

    # Extract data
    extracted_texts = extract_text_with_id(args.xml_file_path)

    # Save to CSV
    save_to_csv(extracted_texts, args.output_csv)

if __name__ == '__main__':
    main()

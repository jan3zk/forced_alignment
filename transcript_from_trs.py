import xml.etree.ElementTree as ET
import sys

def extract_transcription(file_path):
    try:
        tree = ET.parse(file_path)
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

def main():
    if len(sys.argv) != 3:
        print("Usage: python transcript_from_trs.py [path_to_transcription_file] [path_to_output_txt_file]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_path = sys.argv[2]
    transcription = extract_transcription(file_path)
    # Remove all occurrences of "()"
    transcription = transcription.replace("()", "")
    # Remove all occurrences of "+"
    transcription = transcription.replace("+", "")

    try:
        with open(output_path, 'w') as file:
            file.write(transcription)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

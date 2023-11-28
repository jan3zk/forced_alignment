import sys
from utils import extract_transcription

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
            file.write(transcription)e
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

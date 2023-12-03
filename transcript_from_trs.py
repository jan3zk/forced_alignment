import sys
from utils_trs import text_from_trs

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python transcript_from_trs.py [path_to_transcription_file] [path_to_output_txt_file]")
        sys.exit(1)

    trs_path = sys.argv[1]
    txt_path = sys.argv[2]

    transcription = text_from_trs(trs_path)

    # Remove all occurrences of "()"
    transcription = transcription.replace("()", "")
    # Remove all occurrences of "+"
    transcription = transcription.replace("+", "")

    try:
        with open(txt_path, 'w') as file:
            file.write(transcription)
    except Exception as e:
        print(f"Error: {e}")

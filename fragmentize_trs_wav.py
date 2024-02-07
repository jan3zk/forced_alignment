import os
import sys
import subprocess
from utils_tei import intervals_from_tei
from utils_tei import text_from_tei
import shutil

def combine_intervals(intervals, duration):
    """
    Combine text elements from tuples in the list based on the duration input.
    """
    merged_intervals = []
    current_text = ''
    current_start_time = None
    current_end_time = None

    for tmin, tmax, text in intervals:
        # Remove all occurrences of "()"
        text = text.replace("()", "")
        # Remove all occurrences of "+"
        text = text.replace("+", "")
        if current_start_time is None:
            current_start_time = tmin
            current_end_time = tmax
            current_text = text
        elif tmax - duration <= current_start_time:
            current_text += ' ' + text
            current_end_time = tmax
        else:
            merged_intervals.append((current_start_time, current_end_time, current_text))
            current_start_time = tmin
            current_end_time = tmax
            current_text = text

    # Add the last merged text to the list
    if current_text:
        merged_intervals.append((current_start_time, current_end_time, current_text))

    return merged_intervals

def fragmentize_trs_wav(xml_path, wav_path, out_dir, duration):

    # Extract the base name of the trs file without extension
    #base_name = os.path.splitext(os.path.basename(xml_path))[0]
    base_name = os.path.splitext(os.path.basename(wav_path))[0]

    if duration != float('inf'):
        trs_intervals = intervals_from_tei(xml_path, True)
        trs_combined = combine_intervals(trs_intervals, duration)

        # Ensure output directory exists
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # Create txt and corresponding wav files for each combined interval
        for idx, (tmin, tmax, text) in enumerate(trs_combined):
            formatted_tmin = f"{tmin:08.3f}"
            formatted_tmax = f"{tmax:08.3f}"

            # Construct file names
            txt_file_name = f"{base_name}_{formatted_tmin}_{formatted_tmax}_{idx:03d}.txt"
            wav_file_name = f"{base_name}_{formatted_tmin}_{formatted_tmax}_{idx:03d}.wav"
            txt_file_path = os.path.join(out_dir, txt_file_name)
            wav_file_path = os.path.join(out_dir, wav_file_name)

            # Replace '-' for mfa to treat words connected by '-' as separate words
            #text = text.replace('-', ' ')
            # Remove all occurrences of "()"
            text = text.replace("()", "")
            # Remove all occurrences of "+"
            text = text.replace("+", "")

            # Write text file
            with open(txt_file_path, 'w') as file:
                file.write(text)

            # Trim the wav file using ffmpeg
            duration = tmax - tmin
            subprocess.call(['ffmpeg', '-i', wav_path, '-ss', str(tmin), '-t', str(duration), wav_file_path])
    else:
        # Read entire text regardelss of time intervals
        text = text_from_tei(xml_path, True)

        # Write text to file
        txt_file_path = os.path.join(out_dir, base_name+'.txt')
        with open(txt_file_path, 'w') as file:
            file.write(text)

        # Copy wav
        shutil.copy(wav_path, os.path.join(out_dir, base_name+'.wav'))

if __name__ == '__main__':
    """
    This script is designed to process TEI-formatted transcription files (.xml) and corresponding audio files (.wav). 
    It segments both the transcription and audio into smaller, manageable fragments. The segmentation respects sentence 
    boundaries, ensuring that sentences are not split mid-way. Each fragment's duration is guided by the user-specified duration,
    but the script will not break a sentence to adhere to this limit; it may produce segments longer than the desired duration 
    if a sentence exceeds this length.

    The script is intended to be run from the command line and requires four arguments:
        - xml_path: Path to the TEI-formatted transcription file.
        - wav_path: Path to the corresponding audio file.
        - out_dir: Path to the directory where the fragmented transcriptions and audio files will be saved.
        - duration: Target duration for each audio fragment, in seconds. 

    Usage:
        To use the script, execute it with the required parameters. For example:
        python fragmentize_trs.py [path/to/transcription.xml] [path/to/audio.wav] [path/to/output/directory] [duration_in_seconds]

    Note:
        - The script ensures that the output directory exists before saving files.
        - It processes the transcription and audio synchronously, ensuring that each text fragment corresponds to its audio segment.
        - If the duration is set to 'inf' (infinity), the script will process the entire transcription and audio file as a single segment.
    """

    if len(sys.argv) < 5:
        print("Usage: python fragmentize_trs.py [xml_path] [wav_path] [out_dir] [duration]")
        sys.exit(1)

    xml_path = sys.argv[1]
    wav_path = sys.argv[2]
    out_dir = sys.argv[3]
    duration = float(sys.argv[4])  # Convert duration to float

    fragmentize_trs_wav(xml_path, wav_path, out_dir, duration)
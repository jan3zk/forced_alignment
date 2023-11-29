import os
import sys
import subprocess
from utils import intervals_from_trs

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

def fragmentize_trs_wav(trs_path, wav_path, out_dir, duration):
    trs_intervals = intervals_from_trs(trs_path)
    trs_combined = combine_intervals(trs_intervals, duration)

    # Extract the base name of the trs file without extension
    base_name = os.path.splitext(os.path.basename(trs_path))[0]

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
        
        # Write text file
        with open(txt_file_path, 'w') as file:
            file.write(text)

        # Trim the wav file using ffmpeg
        duration = tmax - tmin
        subprocess.call(['ffmpeg', '-i', wav_path, '-ss', str(tmin), '-t', str(duration), wav_file_path])

if __name__ == '__main__':
    # Set up argument parsing
    if len(sys.argv) < 5:
        print("Usage: python fragmentize_trs.py [trs_path] [wav_path] [out_dir] [duration]")
        sys.exit(1)

    trs_path = sys.argv[1]
    wav_path = sys.argv[2]
    out_dir = sys.argv[3]
    duration = float(sys.argv[4])  # Convert duration to float

    fragmentize_trs_wav(trs_path, wav_path, out_dir, duration)

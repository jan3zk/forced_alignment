import os
import sys
import parselmouth
from praatio import textgrid
from collections import defaultdict

def get_average_pitch_for_phonemes(audio_path, textgrid_path, output_path=None):
    # Use Parselmouth to extract pitch values from audio
    sound = parselmouth.Sound(audio_path)
    pitch = sound.to_pitch()
    #pitch_values = pitch.selected_array['frequency']
    time_step = pitch.get_time_step()
    intensity = sound.to_intensity(time_step=time_step)
    intensity_values = intensity.values.squeeze()

    # Use praatio to read the TextGrid
    tg = textgrid.openTextgrid(textgrid_path, False)
    
    # Get the entries of the first tier
    first_tier_name = list(tg._tierDict.keys())[1]
    entry_list = tg._tierDict[first_tier_name].entries

    phoneme_to_avg_intensity = {}
    for start, end, label in entry_list:
        start_index = int(start / time_step)
        end_index = int(end / time_step)
        phoneme_intensity_vals = [val for val in intensity_values[start_index:end_index] if val > 0]
        if phoneme_intensity_vals:
            avg_pitch = sum(phoneme_intensity_vals) / len(phoneme_intensity_vals)
            phoneme_to_avg_intensity[label] = avg_pitch

    # Save to txt file
    if output_path:
        with open(output_path, 'w') as file:
            for phoneme, avg_pitch in phoneme_to_avg_intensity.items():
                file.write(f"{phoneme}\t{avg_pitch}\n")
    
    return phoneme_to_avg_intensity


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python avg_pitch_for_phonemes.py audio_path textgrid_path output_txt_path")
        sys.exit(1)

    audio_path = sys.argv[1]
    textgrid_path = sys.argv[2]
    output_txt_path = sys.argv[3]

    phoneme_pitch_dict = get_average_pitch_for_phonemes(audio_path, textgrid_path, output_txt_path)
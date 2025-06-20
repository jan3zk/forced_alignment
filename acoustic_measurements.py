import os
import sys
import csv
import parselmouth
import numpy as np
from textgrid import TextGrid
from extract_sonority import extract_sonority

def compute_durations(tier):
    return [(interval.mark, "{:.2f}".format(interval.maxTime - interval.minTime)) for interval in tier]

def compute_pitch(input_wav, tier, time_step=0.01, pitch_floor=75, pitch_ceiling=500):
    sound = parselmouth.Sound(input_wav)
    pitch = sound.to_pitch(time_step=time_step, pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling)
    pitch_values = pitch.selected_array['frequency']
    phone_pitches = []
    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        pitch_interval = pitch_values[np.logical_and(pitch.xs() >= start_time, pitch.xs() <= end_time)]
        # Filter out 0 values which represent unvoiced parts
        pitch_interval = pitch_interval[pitch_interval != 0]
        # Calculate the average pitch
        avg_phone_pitch = np.mean(pitch_interval) if len(pitch_interval) > 0 else 0
        phone_pitches.append(round(avg_phone_pitch, 1))
    return phone_pitches

def compute_pitch_trend(input_wav, tier):
    sound = parselmouth.Sound(input_wav)
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    trends = []
    for interval in tier:
        start_index = int(interval.minTime // pitch.time_step)
        end_index = int(interval.maxTime // pitch.time_step)
        pitch_segment = pitch_values[start_index:end_index]
        if all(x < y for x, y in zip(pitch_segment, pitch_segment[1:])):
            trends.append('rising')
        elif all(x > y for x, y in zip(pitch_segment, pitch_segment[1:])):
            trends.append('falling')
        else:
            trends.append('mixed' if len(pitch_segment) > 1 else 'unknown')
    return trends

def compute_formants(input_wav, tier):
    sound = parselmouth.Sound(input_wav)
    formant = sound.to_formant_burg()
    formant_values = {'F1': [], 'F2': [], 'F3': [], 'F4': []}
    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        f1_value = formant.get_value_at_time(1, (start_time + end_time) / 2)  # Get F1 at midpoint
        f2_value = formant.get_value_at_time(2, (start_time + end_time) / 2)  # Get F2 at midpoint
        f3_value = formant.get_value_at_time(3, (start_time + end_time) / 2)  # Get F3 at midpoint
        f4_value = formant.get_value_at_time(4, (start_time + end_time) / 2)  # Get F4 at midpoint
         # Append formant values to respective lists in the dictionary
        formant_values['F1'].append(round(f1_value, 1) if f1_value is not None else 0.0)
        formant_values['F2'].append(round(f2_value, 1) if f2_value is not None else 0.0)
        formant_values['F3'].append(round(f3_value, 1) if f3_value is not None else 0.0)
        formant_values['F4'].append(round(f4_value, 1) if f4_value is not None else 0.0)
    return formant_values

def compute_intensity(input_wav, tier, intensity_threshold=50):
    sound = parselmouth.Sound(input_wav)
    intensity = sound.to_intensity()
    phone_intensities = []
    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        avg_phone_intensity = intensity.get_average(start_time, end_time)
        phone_intensities.append(round(avg_phone_intensity, 1))
    return phone_intensities

def compute_vot(input_wav, tier):
    sound = parselmouth.Sound(input_wav)
    intensity = sound.to_intensity()
    intensity_values = intensity.values[0]  # Assuming one channel
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    vot_values = []
    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        start_index = int(start_time // intensity.time_step)
        end_index = int(end_time // intensity.time_step)
        start_index_pitch = int(start_time // pitch.time_step)
        end_index_pitch = int(end_time // pitch.time_step)
        pitch_interval = pitch_values[start_index_pitch:end_index_pitch]
        # VOT is measured from the end of the phone to the onset of voicing
        cutoff_frequency = 100  # Adjust as needed based on your data
        # Find the first pitch value above the cutoff frequency (indicating voicing onset)
        for i, pitch_value in enumerate(pitch_interval):
            if pitch_value > cutoff_frequency:
                vot = end_time - ((start_index_pitch + i) * pitch.time_step)
                break
        else:
            vot = 0.0  # If voicing onset not found, set VOT to 0.0
        vot_values.append(round(vot, 3))
    return vot_values

def compute_cog(input_wav, tier, power=2):
    snd = parselmouth.Sound(input_wav)
    cog_values = []
    for interval in tier:
        # Extract the audio within the given time interval
        audio_interval = snd.extract_part(from_time=interval.minTime, to_time=interval.maxTime)
        # Calculate the spectral centroid for the audio interval
        spectrum = audio_interval.to_spectrum()
        cog = spectrum.get_center_of_gravity(power)
        cog_values.append(round(cog, 1))
    return cog_values

def compute_sonority(input_wav, tier):
    """Return average sonority for each interval in ``tier``."""
    sonority_vals, sonority_times = extract_sonority(input_wav, plot_graphs=False)
    sonority_values = []
    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        indices = np.logical_and(sonority_times >= start_time, sonority_times <= end_time)
        if np.any(indices):
            avg_sonority = float(np.mean(sonority_vals[indices]))
        else:
            avg_sonority = 0.0
        sonority_values.append(round(avg_sonority, 3))
    return sonority_values

def get_item(tier, item_tier):
    item_list = []
    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        # Find the word that corresponds to the time interval of the phone
        corresponding_item = next((item.mark for item in item_tier if item.minTime <= start_time and item.maxTime >= end_time), '')
        item_list.append(corresponding_item)
    return item_list

def save_to_csv(header, data, output_csv):
    with open(output_csv, mode='w', newline='', encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(zip(*data))

def main(input_textgrid, input_wav, output_csv, level="phones"):
    tg = TextGrid.fromFile(input_textgrid)
    tier = tg.getFirst(level)
    duration = compute_durations(tier)
    pitch = compute_pitch(input_wav, tier)
    pitch_trend = compute_pitch_trend(input_wav, tier)
    intensity = compute_intensity(input_wav, tier)
    sonority = compute_sonority(input_wav, tier)

    if level == "phones":
        formants = compute_formants(input_wav, tier)
        vot = compute_vot(input_wav, tier)
        cog = compute_cog(input_wav, tier)
        previous_phone = [''] + [interval.mark for interval in tier[:-1]]
        next_phone = [interval.mark for interval in tier[1:]] + ['']
        word = get_item(tier, tg.getFirst("strd-wrd-sgmnt"))
        sentence = get_item(tier, tg.getFirst("standardized-trs"))
        speakerID = get_item(tier, tg.getFirst("speaker-ID"))
        audioID = [os.path.splitext(os.path.basename(input_textgrid))[0].replace("-avd",'')] * len(duration)
        csv_data = [('Phone', [t[0] for t in duration]),
            ('Duration', [t[1] for t in duration]),
            ('AvgPitch', pitch),
            ('PitchTrend', pitch_trend),
            ('F1Formant', formants['F1']),
            ('F2Formant', formants['F2']),
            ('F3Formant', formants['F3']),
            ('F4Formant', formants['F4']),
            ('Intensity', intensity),
            ('Sonority', sonority),
            ('VOT', vot),
            ('COG', cog),
            ('PreviousPhone', previous_phone),
            ('NextPhone', next_phone),
            ('Word', word),
            ('Sentence', sentence),
            ('AudioID', audioID),
            ('SpeakerID', speakerID),
        ]

    elif level == "cnvrstl-syllables":
        csv_data = [
            ('Syllable', [d[0] for d in duration]),
            ('Duration', [d[1] for d in duration]),
            ('AvgPitch', pitch),
            ('PitchTrend', pitch_trend),
            ('Intensity', intensity),
            ('Sonority', sonority),
        ]

    save_to_csv( [t[0] for t in csv_data],  [t[1] for t in csv_data], output_csv)
    print(f"Acoustic measurements saved to {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 5:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Usage: python acoustic_measurements.py [input.TextGrid] [input.wav] [output.csv] [level (optional, default='phones')]")

import os
import sys
import csv
import parselmouth
from textgrid import TextGrid

def compute_phone_durations(phone_tier):
    phone_durations = []
    for interval in phone_tier:
        phone = interval.mark
        duration = round(interval.maxTime - interval.minTime, 2)
        phone_durations.append((phone, duration))

    return phone_durations

def compute_phone_pitch(input_wav, phone_tier):
    sound = parselmouth.Sound(input_wav)
    
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']

    phone_pitches = []
    
    for interval in phone_tier:
        start_time = interval.minTime
        end_time = interval.maxTime

        start_index = int(start_time // pitch.time_step)
        end_index = int(end_time // pitch.time_step)
        phone_pitch_values = pitch_values[start_index:end_index]

        if len(phone_pitch_values) > 0:
            avg_phone_pitch = round(sum(phone_pitch_values) / len(phone_pitch_values), 1)
        else:
            avg_phone_pitch = 0.0

        phone_pitches.append(round(avg_phone_pitch, 2))

    return phone_pitches

def compute_pitch_trend(phone_pitch_values):
    # Check if pitch values are rising, falling, or stable within the interval
    if all(x < y for x, y in zip(phone_pitch_values, phone_pitch_values[1:])):
        return 'rising'
    elif all(x > y for x, y in zip(phone_pitch_values, phone_pitch_values[1:])):
        return 'falling'
    else:
        return 'mixed'

def compute_phone_pitch_trend(input_wav, phone_tier):
    sound = parselmouth.Sound(input_wav)
    
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']

    phone_pitch_trends = []
    
    for interval in phone_tier:
        start_time = interval.minTime
        end_time = interval.maxTime

        start_index = int(start_time // pitch.time_step)
        end_index = int(end_time // pitch.time_step)
        phone_pitch_values = pitch_values[start_index:end_index]

        if len(phone_pitch_values) > 1:
            pitch_trend = compute_pitch_trend(phone_pitch_values)
        else:
            pitch_trend = 'unknown'

        phone_pitch_trends.append(pitch_trend)

    return phone_pitch_trends

def compute_f1_formant(input_wav, phone_tier):
    sound = parselmouth.Sound(input_wav)
    formant = sound.to_formant_burg()
    
    formant_values = []
    
    for interval in phone_tier:
        start_time = interval.minTime
        end_time = interval.maxTime

        formant_value = formant.get_value_at_time(1, (start_time + end_time) / 2)  # Get F1 at midpoint
        if formant_value is not None:
            formant_values.append(round(formant_value, 2))
        else:
            formant_values.append(0.0)  # If F1 value is not available, mark it as 0.0
    
    return formant_values

def compute_phone_intensity(input_wav, phone_tier):
    sound = parselmouth.Sound(input_wav)
    
    intensity = sound.to_intensity()
    intensity_values = intensity.values[0]  # Assuming one channel

    phone_intensities = []
    
    for interval in phone_tier:
        start_time = interval.minTime
        end_time = interval.maxTime

        start_index = int(start_time // intensity.time_step)
        end_index = int(end_time // intensity.time_step)
        phone_intensity_values = intensity_values[start_index:end_index]

        if len(phone_intensity_values) > 0:
            avg_phone_intensity = round(sum(phone_intensity_values) / len(phone_intensity_values), 1)
        else:
            avg_phone_pitch = 0.0

        phone_intensities.append(round(avg_phone_intensity, 2))

    return phone_intensities

def compute_vot(input_wav, phone_tier):
    sound = parselmouth.Sound(input_wav)
    
    intensity = sound.to_intensity()
    intensity_values = intensity.values[0]  # Assuming one channel

    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']

    vot_values = []
    
    for interval in phone_tier:
        start_time = interval.minTime
        end_time = interval.maxTime

        start_index = int(start_time // intensity.time_step)
        end_index = int(end_time // intensity.time_step)
        phone_intensity_values = intensity_values[start_index:end_index]

        start_index_pitch = int(start_time // pitch.time_step)
        end_index_pitch = int(end_time // pitch.time_step)
        phone_pitch_values = pitch_values[start_index_pitch:end_index_pitch]

        # Assuming VOT as the time difference between the midpoint of the phone and the onset of voicing
        midpoint = (start_time + end_time) / 2
        cutoff_frequency = 100  # Adjust as needed based on your data

        # Find the first pitch value above the cutoff frequency (indicating voicing onset)
        for i, pitch_value in enumerate(phone_pitch_values):
            if pitch_value > cutoff_frequency:
                vot = midpoint - ((start_index_pitch + i) * pitch.time_step)
                break
        else:
            vot = 0.0  # If voicing onset not found, set VOT to 0.0
        
        vot_values.append(round(vot, 3))

    return vot_values

def compute_cog(input_wav, phone_tier):
    """
    Calculating the Center of Gravity (COG) for each phoneme interval involves determining
    the average frequency weighted by intensity within the specified interval.
    """
    sound = parselmouth.Sound(input_wav)
    
    intensity = sound.to_intensity()
    intensity_values = intensity.values[0]  # Assuming one channel

    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']

    cog_values = []
    
    for interval in phone_tier:
        start_time = interval.minTime
        end_time = interval.maxTime

        start_index = int(start_time // intensity.time_step)
        end_index = int(end_time // intensity.time_step)
        phone_intensity_values = intensity_values[start_index:end_index]

        start_index_pitch = int(start_time // pitch.time_step)
        end_index_pitch = int(end_time // pitch.time_step)
        phone_pitch_values = pitch_values[start_index_pitch:end_index_pitch]

        # Computing COG as a weighted average of pitch values weighted by intensity
        if sum(phone_intensity_values) != 0:  # Check for zero intensity sum
            cog = sum(intensity * pitch for intensity, pitch in zip(phone_intensity_values, phone_pitch_values)) / sum(phone_intensity_values)
        else:
            cog = 0.0  # Assigning COG as 0.0 if intensity sum is zero
        cog_values.append(round(cog, 2))

    return cog_values

def get_item(phone_tier, item_tier):
    item_list = []
    for interval in phone_tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        
        # Find the word that corresponds to the time interval of the phone
        corresponding_item = next((item.mark for item in item_tier if item.minTime <= start_time and item.maxTime >= end_time), '')
        item_list.append(corresponding_item)

    return item_list

def save_to_csv(header_strings, data_lists, output_csv):
    with open(output_csv, mode='w', newline='', encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(header_strings)
        for row in zip(*data_lists):
            writer.writerow(row)

def main(input_textgrid, input_wav, output_csv):
    tg = TextGrid.fromFile(input_textgrid)
    phone_tier = tg.getFirst("phones")

    phone_durations = compute_phone_durations(phone_tier)
    phone_pitches = compute_phone_pitch(input_wav, phone_tier)
    phone_pitch_trends = compute_phone_pitch_trend(input_wav, phone_tier)
    f1_formants = compute_f1_formant(input_wav, phone_tier)
    intensity_values = compute_phone_intensity(input_wav, phone_tier)
    vot_values = compute_vot(input_wav, phone_tier)
    cog_values = compute_cog(input_wav, phone_tier)  # Compute COG
    previous_phoneme = [''] + [interval.mark for interval in phone_tier[:-1]]
    word_list = get_item(phone_tier, tg.getFirst("strd-wrd-sgmnt"))
    sentence_list = get_item(phone_tier, tg.getFirst("standardized-trs"))
    speakerID_list = get_item(phone_tier, tg.getFirst("speaker-ID"))
    audioID_list = [os.path.splitext(os.path.basename(input_textgrid))[0].replace("-avd",'')] * len(phone_durations)

    csv_data = [('Phone', [t[0] for t in phone_durations]),
        ('Duration', [t[1] for t in phone_durations]),
        ('AvgPitch', phone_pitches),
        ('PitchTrend', phone_pitch_trends),
        ('F1Formant', f1_formants),
        ('Intensity', intensity_values),
        ('VOT', vot_values),
        ('COG', cog_values),
        ('PreviousPhone', previous_phoneme),
        ('Word', word_list),
        ('Sentence', sentence_list),
        ('AudioID', audioID_list),
        ('SpeakerID', speakerID_list)]
    save_to_csv( [t[0] for t in csv_data],  [t[1] for t in csv_data], output_csv)
    print(f"Acoustic measurements saved to {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python acoustic_measurements.py [input.TextGrid] [input.wav] [output.csv]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])

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

def save_to_csv(phone_durations, phone_pitches, output_csv):
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Phone', 'Duration', 'Pitch'])
        for i in range(len(phone_durations)):
            writer.writerow([phone_durations[i][0], phone_durations[i][1], phone_pitches[i]])

def main(input_textgrid, input_wav, output_csv):
    # Load the input TextGrid
    tg = TextGrid.fromFile(input_textgrid)
    phone_tier = tg.getFirst("phones")

    phone_durations = compute_phone_durations(phone_tier)
    phone_pitches = compute_phone_pitch(input_wav, phone_tier)

    save_to_csv(phone_durations, phone_pitches, output_csv)
    print(f"Acoustic measurements saved to {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python acoustic_measurements.py [input.TextGrid] [input.wav] [output.csv]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])

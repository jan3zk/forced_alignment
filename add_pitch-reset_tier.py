import sys
import parselmouth
import numpy as np
from textgrid import TextGrid, IntervalTier, Interval

def detect_pitch_resets(audio_path, input_textgrid, output_textgrid, pitch_reset_threshold, method="average-neighboring"):
    # Load the audio and the TextGrid
    sound = parselmouth.Sound(audio_path)
    tg = TextGrid.fromFile(input_textgrid)
    
    # Analyze pitch
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    
    # Get the syllable tier
    syllable_intervals = tg.getFirst("cnvrstl-syllables")
    syllable_intervals = [(interval.minTime, interval.maxTime, interval.mark) for interval in syllable_intervals]
    # Remove empty intervals
    syllable_intervals = [t for t in syllable_intervals if t[-1] != '']

    # Create a new tier for pitch resets
    pitch_reset_intervals = []
    num_intervals = len(syllable_intervals)
    
    for i in range(num_intervals):
        # Get the start and end time of the syllable
        start_time, end_time, _ = syllable_intervals[i]
        
        # Extract pitch values for the current syllable
        start_index = int(start_time // pitch.time_step)
        end_index = int(end_time // pitch.time_step)
        syllable_pitch_values = pitch_values[start_index:end_index]
        syllable_pitch_values = syllable_pitch_values[syllable_pitch_values != 0]  # Remove zero values

        if method == "average-neighboring":
            syllable_mean_pitch = syllable_pitch_values.mean() if len(syllable_pitch_values) > 0 else 0
            
            # Calculate mean pitch of previous and next syllables
            if i > 0 and i < num_intervals - 1:
                prev_start_time, prev_end_time, _ = syllable_intervals[i-1]
                next_start_time, next_end_time, _ = syllable_intervals[i+1]

                prev_syllable_pitch_values = pitch_values[int(prev_start_time // pitch.time_step):int(prev_end_time // pitch.time_step)]
                next_syllable_pitch_values = pitch_values[int(next_start_time // pitch.time_step):int(next_end_time // pitch.time_step)]

                prev_syllable_mean = prev_syllable_pitch_values[prev_syllable_pitch_values != 0].mean() if any(prev_syllable_pitch_values != 0) else 0
                next_syllable_mean = next_syllable_pitch_values[next_syllable_pitch_values != 0].mean() if any(next_syllable_pitch_values != 0) else 0
                
                reference_mean_pitch = (prev_syllable_mean + next_syllable_mean) / 2
            else:
                reference_mean_pitch = syllable_mean_pitch

            # Check for pitch reset
            pitch_reset_occurs = abs(syllable_mean_pitch - reference_mean_pitch) >= pitch_reset_threshold

        elif method == "intrasyllabic":
            if len(syllable_pitch_values) > 1:
                max_pitch = max(syllable_pitch_values)
                min_pitch = min(syllable_pitch_values)
                semitone_difference = 12 * np.log2(max_pitch / min_pitch)
                pitch_reset_occurs = semitone_difference >= 4
            else:
                pitch_reset_occurs = False

        # Label the interval
        label = "POS" if pitch_reset_occurs else "NEG"
        pitch_reset_intervals.append((start_time, end_time, label))
    
    # Add the new tier to the TextGrid
    new_tier = IntervalTier(name="pitch-reset", minTime=min(t[0] for t in pitch_reset_intervals), maxTime=max(t[1] for t in pitch_reset_intervals))
    for start, end, label in pitch_reset_intervals:
        new_tier.addInterval(Interval(start, end, label))
    tg.append(new_tier)

    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python add_pitch-reset_tier.py [input.wav] [input.TextGrid] [output.TextGrid] [pitch_reset_threshold] [method]")
    else:
        detect_pitch_resets(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])

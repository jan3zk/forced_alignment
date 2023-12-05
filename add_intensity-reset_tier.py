import sys
import parselmouth
import numpy as np
from textgrid import TextGrid, IntervalTier, Interval

def detect_intensity_resets(audio_path, input_textgrid, output_textgrid, intensity_reset_threshold=7, method="near", silence_threshold=50):
    # Load the audio and the TextGrid
    sound = parselmouth.Sound(audio_path)
    tg = TextGrid.fromFile(input_textgrid)
    
    # Analyze intensity
    intensity = sound.to_intensity()
    intensity_values = intensity.values[0]  # Assuming one channel

    # Get the syllable tier
    syllable_intervals = tg.getFirst("cnvrstl-syllables")
    syllable_intervals = [(interval.minTime, interval.maxTime, interval.mark) for interval in syllable_intervals]
    # Remove empty intervals
    syllable_intervals = [t for t in syllable_intervals if t[-1] != '']
    
    # Create a new tier for intensity resets
    intensity_reset_intervals = []
    num_intervals = len(syllable_intervals)
    
    for i in range(num_intervals):
        # Get the start and end time of the syllable
        start_time, end_time, _ = syllable_intervals[i]
        
        # Extract intensity values for the current syllable
        start_index = int(start_time // intensity.time_step)
        end_index = int(end_time // intensity.time_step)
        syllable_intensity_values = intensity_values[start_index:end_index]
        syllable_intensity_values = syllable_intensity_values[syllable_intensity_values > silence_threshold]  # Include only values greater than silence_threshold, i.e. exclude non-speach parts
        syllable_mean_intensity = syllable_intensity_values.mean() if len(syllable_intensity_values) > 0 else 0

        if method == "near":
            # Calculate mean intensity of the nearest neighbors
            neighbors_mean_intensity = []
            for j in range(max(0, i-1), min(i+2, num_intervals)):
                if j != i:
                    neighbor_start_time, neighbor_end_time, _ = syllable_intervals[j]
                    neighbor_intensity_values = intensity_values[int(neighbor_start_time // intensity.time_step):int(neighbor_end_time // intensity.time_step)]
                    neighbor_intensity_values = neighbor_intensity_values[neighbor_intensity_values > silence_threshold]  # Include only valus greater than silence_threshold dB
                    neighbors_mean_intensity.append(neighbor_intensity_values.mean() if len(neighbor_intensity_values) > 0 else 0)

            reference_mean_intensity = np.mean(neighbors_mean_intensity) if neighbors_mean_intensity else syllable_mean_intensity

        elif method == "extended":
            # Calculate mean intensity of the nearest four neighbors
            neighbors_mean_intensity = []
            for j in range(max(0, i-2), min(i+3, num_intervals)):
                if j != i:
                    neighbor_start_time, neighbor_end_time, _ = syllable_intervals[j]
                    neighbor_intensity_values = intensity_values[int(neighbor_start_time // intensity.time_step):int(neighbor_end_time // intensity.time_step)]
                    neighbor_intensity_values = neighbor_intensity_values[neighbor_intensity_values > silence_threshold]  # Include only valus greater than silence_threshold dB
                    neighbors_mean_intensity.append(neighbor_intensity_values.mean() if len(neighbor_intensity_values) > 0 else 0)

            reference_mean_intensity = np.mean(neighbors_mean_intensity) if neighbors_mean_intensity else syllable_mean_intensity

        # Check for intensity reset
        intensity_reset_occurs = abs(syllable_mean_intensity - reference_mean_intensity) >= intensity_reset_threshold

        # Label the interval
        label = "POS" if intensity_reset_occurs else "NEG"
        intensity_reset_intervals.append((start_time, end_time, label))

    # Add the new tier to the TextGrid
    new_tier = IntervalTier(name="intensity-reset", minTime=min(t[0] for t in intensity_reset_intervals), maxTime=max(t[1] for t in intensity_reset_intervals))
    for start, end, label in intensity_reset_intervals:
        new_tier.addInterval(Interval(start, end, label))
    tg.append(new_tier)

    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python add_intensity-reset_tier.py [input.wav] [input.TextGrid] [output.TextGrid] [intensity_reset_threshold] [method]")
    else:
        detect_intensity_resets(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])

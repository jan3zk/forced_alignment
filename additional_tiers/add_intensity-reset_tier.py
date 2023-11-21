import sys
import parselmouth
import numpy as np
from utils import parse_textgrid, write_textgrid

def detect_intensity_resets(audio_path, input_textgrid, output_textgrid, intensity_reset_threshold=7, method="near"):
    # Load the audio and the TextGrid
    sound = parselmouth.Sound(audio_path)
    tiers = parse_textgrid(input_textgrid)
    
    # Analyze intensity
    intensity = sound.to_intensity()
    intensity_values = intensity.values[0]  # Assuming one channel

    # Get the syllable tier
    syllable_tier = tiers['cnvrstl-syllables']
    
    # Create a new tier for intensity resets
    intensity_reset_tier = []
    num_intervals = len(syllable_tier)
    
    for i in range(num_intervals):
        # Get the start and end time of the syllable
        start_time, end_time, _ = syllable_tier[i]
        
        # Extract intensity values for the current syllable
        start_index = int(start_time // intensity.time_step)
        end_index = int(end_time // intensity.time_step)
        syllable_intensity_values = intensity_values[start_index:end_index]
        syllable_intensity_values = syllable_intensity_values[syllable_intensity_values > 50]  # Include only valus greater than 50 dB
        syllable_mean_intensity = syllable_intensity_values.mean() if len(syllable_intensity_values) > 0 else 0

        if method == "near":
            # Calculate mean intensity of the nearest neighbors
            neighbors_mean_intensity = []
            for j in range(max(0, i-1), min(i+2, num_intervals)):
                if j != i:
                    neighbor_start_time, neighbor_end_time, _ = syllable_tier[j]
                    neighbor_intensity_values = intensity_values[int(neighbor_start_time // intensity.time_step):int(neighbor_end_time // intensity.time_step)]
                    neighbor_intensity_values = neighbor_intensity_values[neighbor_intensity_values > 50]  # Include only valus greater than 50 dB
                    neighbors_mean_intensity.append(neighbor_intensity_values.mean() if len(neighbor_intensity_values) > 0 else 0)

            reference_mean_intensity = np.mean(neighbors_mean_intensity) if neighbors_mean_intensity else syllable_mean_intensity

        elif method == "extended":
            # Calculate mean intensity of the nearest four neighbors
            neighbors_mean_intensity = []
            for j in range(max(0, i-2), min(i+3, num_intervals)):
                if j != i:
                    neighbor_start_time, neighbor_end_time, _ = syllable_tier[j]
                    neighbor_intensity_values = intensity_values[int(neighbor_start_time // intensity.time_step):int(neighbor_end_time // intensity.time_step)]
                    neighbor_intensity_values = neighbor_intensity_values[neighbor_intensity_values > 50]  # Include only valus greater than 50 dB
                    neighbors_mean_intensity.append(neighbor_intensity_values.mean() if len(neighbor_intensity_values) > 0 else 0)

            reference_mean_intensity = np.mean(neighbors_mean_intensity) if neighbors_mean_intensity else syllable_mean_intensity

        # Check for intensity reset
        intensity_reset_occurs = abs(syllable_mean_intensity - reference_mean_intensity) >= intensity_reset_threshold

        # Label the interval
        label = "POS" if intensity_reset_occurs else "NEG"
        intensity_reset_tier.append((start_time, end_time, label))
    
    # Add the new tier to the TextGrid
    tiers['intensity-reset'] = intensity_reset_tier
    
    # Save the modified TextGrid
    write_textgrid(output_textgrid, tiers)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python add_intensity-reset_tier.py [input.wav] [input.TextGrid] [output.TextGrid] [intensity_reset_threshold] [method]")
    else:
        detect_intensity_resets(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])

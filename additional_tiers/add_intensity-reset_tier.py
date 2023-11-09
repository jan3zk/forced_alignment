import sys
import parselmouth
from utils import parse_textgrid, write_textgrid  


def detect_intensity_resets(audio_path, input_textgrid, output_textgrid, intensity_reset_threshold=5):
    # Load the audio and the TextGrid
    sound = parselmouth.Sound(audio_path)
    tiers = parse_textgrid(input_textgrid)
    
    # Analyze intensity
    intensity = sound.to_intensity()
    intensity_values = intensity.values.flatten()
    
    # Get the syllable tier
    syllable_tier = tiers['cnvrstl-syllables']
    
    # Create a new tier for intensity resets
    intensity_reset_tier = []
    num_intervals = len(syllable_tier)
    
    previous_syllable_mean_intensity = None
    
    for i in range(num_intervals):
        # Get the start and end time of the syllable
        start_time, end_time, _ = syllable_tier[i]
        
        # Extract intensity values for the current syllable
        start_index = int(start_time // intensity.dt)
        end_index = int(end_time // intensity.dt)
        syllable_intensity_values = intensity_values[start_index:end_index]
        syllable_mean_intensity = syllable_intensity_values.mean() if len(syllable_intensity_values) > 0 else 0
        
        # Check for intensity reset
        intensity_reset_occurs = (
            previous_syllable_mean_intensity is not None and
            syllable_mean_intensity - previous_syllable_mean_intensity >= intensity_reset_threshold
        )
        
        # Label the interval
        label = "POS" if intensity_reset_occurs else "NEG"
        intensity_reset_tier.append((start_time, end_time, label))
        
        # Update the previous syllable mean intensity
        previous_syllable_mean_intensity = syllable_mean_intensity
    
    # Add the new tier to the TextGrid
    tiers['intensity-reset'] = intensity_reset_tier
    
    # Save the modified TextGrid
    write_textgrid(output_textgrid, tiers)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python add_intensity-reset_tier.py [input.wav] [input.TextGrid] [output.TextGrid] [intensity_reset_threshold]")
    else:
        detect_intensity_resets(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]))


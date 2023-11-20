import sys
import parselmouth
from utils import parse_textgrid, write_textgrid  

def detect_pitch_resets(audio_path, input_textgrid, output_textgrid, pitch_reset_threshold=40):
    # Load the audio and the TextGrid
    sound = parselmouth.Sound(audio_path)
    tiers = parse_textgrid(input_textgrid)
    
    # Analyze pitch
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    
    # Get the syllable tier
    syllable_tier = tiers['cnvrstl-syllables']
    
    # Create a new tier for pitch resets
    pitch_reset_tier = []
    num_intervals = len(syllable_tier)
    
    for i in range(num_intervals):
        # Get the start and end time of the syllable
        start_time, end_time, _ = syllable_tier[i]
        
        # Extract pitch values for the current syllable
        start_index = int(start_time // pitch.time_step)
        end_index = int(end_time // pitch.time_step)
        syllable_pitch_values = pitch_values[start_index:end_index]
        syllable_mean_pitch = syllable_pitch_values[syllable_pitch_values != 0].mean() if any(syllable_pitch_values != 0) else 0
        
        # Calculate mean pitch of previous and next syllables
        if i > 0 and i < num_intervals - 1:
            prev_start_time, prev_end_time, _ = syllable_tier[i-1]
            next_start_time, next_end_time, _ = syllable_tier[i+1]

            prev_syllable_pitch_values = pitch_values[int(prev_start_time // pitch.time_step):int(prev_end_time // pitch.time_step)]
            next_syllable_pitch_values = pitch_values[int(next_start_time // pitch.time_step):int(next_end_time // pitch.time_step)]

            prev_syllable_mean = prev_syllable_pitch_values[prev_syllable_pitch_values != 0].mean() if any(prev_syllable_pitch_values != 0) else 0
            next_syllable_mean = next_syllable_pitch_values[next_syllable_pitch_values != 0].mean() if any(next_syllable_pitch_values != 0) else 0
            
            reference_mean_pitch = (prev_syllable_mean + next_syllable_mean) / 2
        else:
            reference_mean_pitch = syllable_mean_pitch

        # Check for pitch reset
        pitch_reset_occurs = abs(syllable_mean_pitch - reference_mean_pitch) >= pitch_reset_threshold

        # Label the interval
        label = "POS" if pitch_reset_occurs else "NEG"
        pitch_reset_tier.append((start_time, end_time, label))
    
    # Add the new tier to the TextGrid
    tiers['pitch-reset'] = pitch_reset_tier
    
    # Save the modified TextGrid
    write_textgrid(output_textgrid, tiers)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python add_pitch-reset_tier.py [input.wav] [input.TextGrid] [output.TextGrid] [pitch_reset_threshold]")
    else:
        detect_pitch_resets(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))

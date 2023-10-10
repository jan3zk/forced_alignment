import sys
import parselmouth
from parselmouth.praat import call
from add_syllable_tier import parse_textgrid, write_textgrid  


def detect_pitch_resets(audio_path, textgrid_path, new_textgrid_path, pitch_reset_threshold=30):
    # Load the audio and the TextGrid
    sound = parselmouth.Sound(audio_path)
    with open(textgrid_path, "r") as file:
        textgrid_content = file.read()
    textgrid = parse_textgrid(textgrid_content)
    
    # Analyze pitch
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    
    # Get the syllable tier
    syllable_tier = textgrid['syllables']
    
    # Create a new tier for pitch resets
    pitch_reset_tier = []
    num_intervals = len(syllable_tier)
    
    previous_syllable_mean_pitch = None
    
    for i in range(num_intervals):
        # Get the start and end time of the syllable
        start_time, end_time, _ = syllable_tier[i]
        
        # Extract pitch values for the current syllable
        start_index = int(start_time // pitch.time_step)
        end_index = int(end_time // pitch.time_step)
        syllable_pitch_values = pitch_values[start_index:end_index]
        syllable_mean_pitch = syllable_pitch_values[syllable_pitch_values != 0].mean() if any(syllable_pitch_values != 0) else 0
        
        # Check for pitch reset
        pitch_reset_occurs = (
            previous_syllable_mean_pitch is not None and
            syllable_mean_pitch - previous_syllable_mean_pitch >= pitch_reset_threshold
        )
        
        # Label the interval
        label = "POS" if pitch_reset_occurs else "NEG"
        pitch_reset_tier.append((start_time, end_time, label))
        
        # Update the previous syllable mean pitch
        previous_syllable_mean_pitch = syllable_mean_pitch
    
    # Add the new tier to the TextGrid
    textgrid['pitch reset'] = pitch_reset_tier
    
    # Save the modified TextGrid
    write_textgrid(new_textgrid_path, textgrid)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python add_pitch_reset_tier.py [audio_path] [textgrid_path] [new_textgrid_path] [pitch_reset_threshold]")
    else:
        detect_pitch_resets(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

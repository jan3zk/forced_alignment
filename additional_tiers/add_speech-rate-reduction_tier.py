import sys
import parselmouth
from utils import parse_textgrid, write_textgrid  

def detect_speech_rate_reduction(audio_path, input_textgrid, output_textgrid, reduction_threshold=0.5):
    # Load the audio and the TextGrid
    sound = parselmouth.Sound(audio_path)
    tiers = parse_textgrid(input_textgrid)
    
    # Get the syllable tier (assuming it is named 'syllables' in the TextGrid)
    syllable_tier = tiers.get('cnvrstl-syllables', [])

    # Create a new tier for speech rate reduction
    speech_rate_reduction_tier = []
    previous_end_time = 0
    previous_rate = 0

    for i, (start_time, end_time, _) in enumerate(syllable_tier):
        # Calculate the speech rate as syllables per second
        if i == 0:
            previous_end_time = end_time
            continue  # Skip the first syllable as we need a pair to compare the rate
        
        # Calculate duration between the end of the previous syllable and the end of the current syllable
        duration = end_time - previous_end_time
        # Check for zero or negative duration to avoid division by zero or incorrect values
        if duration <= 0:
            continue

        # Calculate the current speech rate
        current_rate = 1 / duration
        
        # Check for speech rate reduction (we invert the threshold as we're looking for a decrease)
        rate_reduction_occurs = (previous_rate - current_rate) >= reduction_threshold
        
        # Label the interval
        label = "POS" if rate_reduction_occurs else "NEG"
        speech_rate_reduction_tier.append((start_time, end_time, label))
        
        # Update the previous values
        previous_end_time = end_time
        previous_rate = current_rate
    
    # Add the new tier to the TextGrid
    tiers['speech-rate-reduction'] = speech_rate_reduction_tier
    
    # Save the modified TextGrid
    write_textgrid(output_textgrid, tiers)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python add_speech-rate-reduction_tier.py [input.wav] [input.TextGrid] [output.TextGrid] [reduction_threshold]")
    else:
        detect_speech_rate_reduction(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]))

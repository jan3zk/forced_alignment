import sys
import parselmouth
from utils import parse_textgrid, write_textgrid  

def detect_speech_rate_reduction(audio_path, input_textgrid, output_textgrid, reduction_threshold, method="near"):
    # Load the audio and the TextGrid
    sound = parselmouth.Sound(audio_path)
    tiers = parse_textgrid(input_textgrid)
    
    # Get the syllable tier (assuming it is named 'cnvrstl-syllables' in the TextGrid)
    syllable_tier = tiers.get('cnvrstl-syllables', [])

    # Create a new tier for speech rate reduction
    speech_rate_reduction_tier = []

    for i, (start_time, end_time, _) in enumerate(syllable_tier):
        # Calculate the length of the current syllable
        syllable_length = end_time - start_time
        
        neighbors = []
        if method == "near":
            range_indices = range(max(0, i-1), min(len(syllable_tier), i+2))
        elif method == "extended":
            range_indices = range(max(0, i-2), min(len(syllable_tier), i+3))

        for j in range_indices:
            if j != i:
                neighbor_start_time, neighbor_end_time, _ = syllable_tier[j]
                neighbor_length = neighbor_end_time - neighbor_start_time
                neighbors.append(neighbor_length)
        
        average_neighbor_length = sum(neighbors) / len(neighbors) if neighbors else 0

        # Check for speech rate reduction
        rate_reduction_occurs = syllable_length > (average_neighbor_length * reduction_threshold)

        # Label the interval
        label = "POS" if rate_reduction_occurs else "NEG"
        speech_rate_reduction_tier.append((start_time, end_time, label))

    # Add the new tier to the TextGrid
    tiers['speech-rate-reduction'] = speech_rate_reduction_tier
    
    # Save the modified TextGrid
    write_textgrid(output_textgrid, tiers)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python add_speech-rate-reduction_tier.py [input.wav] [input.TextGrid] [output.TextGrid] [reduction_threshold] [method]")
    else:
        detect_speech_rate_reduction(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5])

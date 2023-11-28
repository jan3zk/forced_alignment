import sys
import parselmouth
from textgrid import TextGrid, IntervalTier, Interval

def detect_speech_rate_reduction(audio_path, input_textgrid, output_textgrid, reduction_threshold, method="near"):
    # Load the audio and the TextGrid
    sound = parselmouth.Sound(audio_path)
    tg = TextGrid.fromFile(input_textgrid)
    
    # Get the syllable tier (assuming it is named 'cnvrstl-syllables' in the TextGrid)
    syllable_intervals = tg.getFirst("cnvrstl-syllables")
    syllable_intervals = [(interval.minTime, interval.maxTime, interval.mark) for interval in syllable_intervals]
    # Remove empty intervals
    syllable_intervals = [t for t in syllable_intervals if t[-1] != '']

    # Create a new tier for speech rate reduction
    speech_rate_reduction_intervals = []

    for i, (start_time, end_time, _) in enumerate(syllable_intervals):
        # Calculate the length of the current syllable
        syllable_length = end_time - start_time
        
        neighbors = []
        if method == "near":
            range_indices = range(max(0, i-1), min(len(syllable_intervals), i+2))
        elif method == "extended":
            range_indices = range(max(0, i-2), min(len(syllable_intervals), i+3))

        for j in range_indices:
            if j != i:
                neighbor_start_time, neighbor_end_time, _ = syllable_intervals[j]
                neighbor_length = neighbor_end_time - neighbor_start_time
                neighbors.append(neighbor_length)
        
        average_neighbor_length = sum(neighbors) / len(neighbors) if neighbors else 0

        # Check for speech rate reduction
        rate_reduction_occurs = syllable_length > (average_neighbor_length * reduction_threshold)

        # Label the interval
        label = "POS" if rate_reduction_occurs else "NEG"
        speech_rate_reduction_intervals.append((start_time, end_time, label))

    # Add the new tier to the TextGrid
    new_tier = IntervalTier(name="speech-rate-reduction", minTime=min(t[0] for t in speech_rate_reduction_intervals), maxTime=max(t[1] for t in speech_rate_reduction_intervals))
    for start, end, label in speech_rate_reduction_intervals:
        new_tier.addInterval(Interval(start, end, label))
    tg.append(new_tier)

    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python add_speech-rate-reduction_tier.py [input.wav] [input.TextGrid] [output.TextGrid] [reduction_threshold] [method]")
    else:
        detect_speech_rate_reduction(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5])

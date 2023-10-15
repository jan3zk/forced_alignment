import sys
from utils import parse_textgrid, write_textgrid
from collections import OrderedDict


def get_speaker(start_time, end_time, speaker_intervals):
    max_overlap = 0
    max_overlap_speaker = None
    
    for sp_start, sp_end, speaker_label in speaker_intervals:
        overlap = min(end_time, sp_end) - max(start_time, sp_start)
        if overlap > max_overlap:
            max_overlap = overlap
            max_overlap_speaker = speaker_label
    
    return max_overlap_speaker

def detect_speaker_change(tiers):
    syl_intervals = tiers.get('cnvrstl-syllables', [])
    speaker_intervals = tiers.get('speaker-ID', [])
    speaker_change_tier = []

    for i, (start, end, _) in enumerate(syl_intervals):
        current_speaker = get_speaker(start, end, speaker_intervals)

        # Check if adjacent intervals are available and extract their speakers
        prev_speaker = get_speaker(*syl_intervals[i-1][:2], speaker_intervals) if i > 0 else None
        next_speaker = get_speaker(*syl_intervals[i+1][:2], speaker_intervals) if i < len(syl_intervals) - 1 else None
        
        # Determine if there is a speaker change
        is_change = (
            (prev_speaker is not None and current_speaker != prev_speaker) or 
            (next_speaker is not None and current_speaker != next_speaker)
        )
        label = 'POS' if is_change else 'NEG'
        
        # Append to the speaker_change_tier
        speaker_change_tier.append((start, end, label))

    return speaker_change_tier


def main(input_textgrid, output_textgrid):
    # Load and parse the TextGrid file
    tiers = parse_textgrid(input_textgrid)

    speaker_change_tier = detect_speaker_change(tiers)

    # Add the new tier to the TextGrid
    tiers['speaker-change'] = speaker_change_tier
    
    # Save the modified TextGrid
    write_textgrid(output_textgrid, tiers)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_speaker-change_tier.py [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2])

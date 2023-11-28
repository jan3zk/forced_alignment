import sys
from textgrid import TextGrid, IntervalTier, Interval

def get_speaker(start_time, end_time, speaker_intervals):
    max_overlap = 0
    max_overlap_speaker = None
    
    for sp_start, sp_end, speaker_label in speaker_intervals:
        overlap = min(end_time, sp_end) - max(start_time, sp_start)
        if overlap > max_overlap:
            max_overlap = overlap
            max_overlap_speaker = speaker_label
    
    return max_overlap_speaker

def detect_speaker_change(syl_intervals, speaker_intervals):
    speaker_change_tier = []

    for i, (start, end, _) in enumerate(syl_intervals):
        current_speaker = get_speaker(start, end, speaker_intervals)

        # Check if adjacent intervals are available and extract their speakers
        prev_speaker = get_speaker(*syl_intervals[i-1][:2], speaker_intervals) if i > 0 else ''
        next_speaker = get_speaker(*syl_intervals[i+1][:2], speaker_intervals) if i < len(syl_intervals) - 1 else ''
        
        # Determine if there is a speaker change
        is_change = current_speaker!='' and     ((prev_speaker!='' and current_speaker != prev_speaker) or (next_speaker!='' and current_speaker != next_speaker))
        
        label = 'POS' if is_change else 'NEG'
        
        # Append to the speaker_change_tier
        speaker_change_tier.append((start, end, label))

    return speaker_change_tier

def main(input_textgrid, output_textgrid):
    # Load and parse the TextGrid file
    tg = TextGrid.fromFile(input_textgrid)

    syl_intervals = tg.getFirst("cnvrstl-syllables")
    syl_intervals = [(interval.minTime, interval.maxTime, interval.mark) for interval in syl_intervals]
    # Remove empty or whitespace-only intervals
    syl_intervals = [interval for interval in syl_intervals if interval[2].strip()]

    speaker_intervals = tg.getFirst("speaker-ID")
    speaker_intervals = [(interval.minTime, interval.maxTime, interval.mark) for interval in speaker_intervals]

    speaker_change_tier = detect_speaker_change(syl_intervals, speaker_intervals)

    # Add the new tier to the TextGrid
    new_tier = IntervalTier(name="speaker-change", minTime=min(t[0] for t in speaker_change_tier), maxTime=max(t[1] for t in speaker_change_tier))
    for start, end, label in speaker_change_tier:
        new_tier.addInterval(Interval(start, end, label))
    tg.append(new_tier)

    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_speaker-change_tier.py [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2])

import sys
from pyannote.audio import Pipeline
import torch
from utils import parse_textgrid, write_textgrid
from collections import OrderedDict


def concatenate_intervals(intervals):
    speakers = set(speaker for _, _, speaker in intervals)
    speaker_intervals = {}
    
    for speaker in speakers:
        speaker_intervals_raw = [(start, end) for start, end, spkr in intervals if spkr == speaker]
        min_start = min(start for start, _ in speaker_intervals_raw)
        max_end = max(end for _, end in speaker_intervals_raw)
        speaker_intervals[speaker] = (min_start, max_end)
    
    return [(start, end, speaker) for speaker, (start, end) in speaker_intervals.items()]


def main(input_wav, input_textgrid, output_textgrid, auth_token):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.0",
        use_auth_token=auth_token)
    
    # send pipeline to GPU (when available)
    pipeline.to(torch.device("cuda"))
    
    # apply pretrained pipeline
    diarization = pipeline(input_wav)
    
    # Convert diarization result to intervals format
    intervals = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        intervals.append((turn.start, turn.end, speaker))    

    # Concatenate adjacent intervals belonging to the same speaker
    concatenated_intervals = concatenate_intervals(intervals)
    
    # Load and parse the TextGrid file
    tiers = parse_textgrid(input_textgrid)
    
    # Add the new speaker tier as the first tier
    extended_tiers = OrderedDict()
    extended_tiers['speaker-ID'] = concatenated_intervals
    extended_tiers.update(tiers)

    # Write the modified TextGrid content to a new file
    write_textgrid(output_textgrid, extended_tiers)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python add_speaker-ID_tier.py [input.wav] [input.TextGrid] [output.TextGrid] [auth_token]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

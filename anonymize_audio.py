import xml.etree.ElementTree as ET
from pydub import AudioSegment
from pydub.generators import Sine
import numpy as np
import argparse
from pathlib import Path
import sys
from textgrid import TextGrid
from numpy import inf
import spacy

def get_audio_level(audio_segment, start_ms, end_ms, window_ms=500):
    """Calculate the average volume of audio in a window around the given interval."""
    window_start = max(0, start_ms - window_ms)
    window_end = min(len(audio_segment), end_ms + window_ms)
    
    surrounding_audio = audio_segment[window_start:window_end]
    return surrounding_audio.rms

def generate_beep(duration_ms, target_rms, frequency=1000):
    """Generate a beep sound of given duration, frequency, and volume."""
    samples = np.sin(2 * np.pi * frequency * np.arange(duration_ms * 44.1) / 44100)
    samples = (samples * 32767).astype(np.int16)
    beep = AudioSegment(
        samples.tobytes(), 
        frame_rate=44100,
        sample_width=2,
        channels=1
    )
    
    current_rms = beep.rms
    if current_rms > 0:
        gain_change = target_rms / current_rms
        gain_change *= 0.7
        beep = beep.apply_gain(20 * np.log10(gain_change))
    
    return beep

def apply_fade(audio_segment, duration_ms):
    """Safely apply fade in and fade out to an audio segment."""
    if duration_ms <= 0:
        return audio_segment
    
    try:
        return audio_segment.fade_in(duration_ms).fade_out(duration_ms)
    except:
        return audio_segment

# TextGrid mode functions
def get_intervals(input_textgrid):
    tg = TextGrid.fromFile(input_textgrid)
    intervals = []
    for interval in tg.getFirst('strd-wrd-sgmnt'):
        intervals.append((interval.minTime, interval.maxTime, interval.mark))
    return intervals

def identify_names(text):
    nlp = spacy.load("sl_core_news_trf")
    doc = nlp(text)
    names = [ent.text for ent in doc.ents if ent.label_ == "PER"]
    return names

def flexible_compare(input_string, pattern):
    if pattern.endswith('*'):
        prefix = pattern[:-1]
        return input_string.startswith(prefix)
    else:
        return input_string == pattern

def find_next_turn_start_time(turn, root):
    """Find the start time of the next Turn element."""
    # Get all turns
    all_turns = root.findall(".//Turn")
    # Find current turn's index
    for i, t in enumerate(all_turns):
        if t == turn and i < len(all_turns) - 1:
            return float(all_turns[i + 1].get('startTime'))
    return None

def parse_trs_file(trs_path):
    """Extract background intervals from TRS file."""
    tree = ET.parse(trs_path)
    root = tree.getroot()
    
    background_intervals = []
    
    # Find all Turns
    for turn in root.findall(".//Turn"):
        elements = list(turn)
        i = 0
        while i < len(elements):
            elem = elements[i]
            if elem.tag == 'Background' and elem.get('type') == 'shh' and elem.get('level') == 'high':
                start_time = float(elem.get('time'))
                text = None
                if elem.tail is not None:
                    text = elem.tail.strip()
                
                # Find the closing Background tag - only check for level="off"
                end_time = None
                for j in range(i + 1, len(elements)):
                    next_elem = elements[j]
                    if next_elem.tag == 'Background' and next_elem.get('level') == 'off':
                        end_time = float(next_elem.get('time'))
                        i = j  # Skip to the closing tag
                        break
                
                # If no explicit end time found or start == end, use next turn's start time or current turn's end time
                if end_time is None or end_time == start_time:
                    next_turn_start = find_next_turn_start_time(turn, root)
                    if next_turn_start:
                        end_time = next_turn_start
                    else:
                        # Use current turn's end time
                        end_time = float(turn.get('endTime'))
                
                # Only check if end_time is valid and greater than start_time
                if end_time and end_time > start_time:
                    # Use empty string if no text is present
                    text = text if text else ""
                    background_intervals.append((
                        int(start_time * 1000),
                        int(end_time * 1000),
                        text
                    ))
            i += 1
    
    print(f"Found {len(background_intervals)} background intervals to anonymize:")
    for start, end, text in background_intervals:
        print(f"  {start}ms - {end}ms (duration: {end-start}ms)")
        if text:
            print(f"  Text to anonymize: {text}")
        else:
            print("  No text associated with this interval")
    
    return background_intervals

def anonymize_audio_textgrid(input_wav, input_textgrid, output_wav, keywords=[]):
    """Anonymize audio using TextGrid mode."""
    intervals = get_intervals(input_textgrid)
    
    if not keywords:
        text = " ".join([tup[-1] for tup in intervals])
        keywords = identify_names(text)
        keywords = [word for item in keywords for word in item.split()]
        keywords = list(set(keywords))
        print(f"Identified keywords containing personal information: {keywords}")
    
    audio = AudioSegment.from_wav(input_wav)
    anonymized_intervals = []
    
    for xmin, xmax, text in intervals:
        for keyword in keywords:
            if flexible_compare(text.lower(), keyword.lower()):
                print(f"Anonymizing part from {xmin}s to {xmax}s: {text}")
                duration_ms = int((xmax - xmin) * 1000)
                target_rms = get_audio_level(audio, int(xmin * 1000), int(xmax * 1000))
                beep = generate_beep(duration_ms, target_rms)
                
                # Apply fade
                fade_ms = min(10, duration_ms // 4)
                if fade_ms > 0:
                    beep = apply_fade(beep, fade_ms)
                    
                audio = audio.overlay(beep, position=int(xmin * 1000))
                anonymized_intervals.append((xmin, xmax, text))
    
    audio.export(output_wav, format='wav')
    print(f"Anonymized audio saved to: {output_wav}")
    return anonymized_intervals

def anonymize_audio_trs(input_wav, input_trs, output_wav):
    """Anonymize audio using TRS mode."""
    audio = AudioSegment.from_wav(input_wav)
    intervals = parse_trs_file(input_trs)
    
    for start_ms, end_ms, text in intervals:
        duration_ms = end_ms - start_ms
        target_rms = get_audio_level(audio, start_ms, end_ms)
        beep = generate_beep(duration_ms, target_rms)
        
        fade_ms = min(10, duration_ms // 4)
        if fade_ms > 0:
            beep = apply_fade(beep, fade_ms)
        
        audio = audio[:start_ms] + beep + audio[end_ms:]
    
    audio.export(output_wav, format='wav')
    print(f"Anonymized audio saved to: {output_wav}")

def main():
    parser = argparse.ArgumentParser(description='Audio anonymizer with TextGrid and TRS support')
    parser.add_argument('mode', choices=['textgrid', 'trs'], help='Anonymization mode (textgrid or trs)')
    parser.add_argument('input_wav', help='Input WAV file')
    parser.add_argument('input_file', help='Input TextGrid or TRS file')
    parser.add_argument('output_wav', help='Output WAV file')
    parser.add_argument('--keywords', nargs='*', help='Keywords to anonymize (TextGrid mode only), e.g. [*, to anonymize all text in square brackets')
    
    args = parser.parse_args()
    
    # Ensure input files exist
    if not Path(args.input_wav).exists():
        raise FileNotFoundError(f"WAV file not found: {args.input_wav}")
    if not Path(args.input_file).exists():
        raise FileNotFoundError(f"Input file not found: {args.input_file}")
    
    # Create output directory if it doesn't exist
    Path(args.output_wav).parent.mkdir(parents=True, exist_ok=True)
    
    if args.mode == 'textgrid':
        anonymize_audio_textgrid(args.input_wav, args.input_file, args.output_wav, args.keywords)
    else:  # trs mode
        anonymize_audio_trs(args.input_wav, args.input_file, args.output_wav)

if __name__ == "__main__":
    main()
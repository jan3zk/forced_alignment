import sys
import wave
import contextlib
from pydub import AudioSegment
from pydub.generators import Sine
from textgrid import TextGrid
from numpy import inf
import spacy

    # Load spaCy model for NER
nlp = spacy.load("sl_core_news_trf")

def get_intervals(input_textgrid):
    tg = TextGrid.fromFile(input_textgrid)
    intervals = []
    for interval in tg.getFirst('strd-wrd-sgmnt'):
        intervals.append((interval.minTime, interval.maxTime, interval.mark))
    return intervals

def identify_names(text):
    doc = nlp(text)
    names = [ent.text for ent in doc.ents if ent.label_ == "PER"]
    return names

def flexible_compare(input_string, pattern):
    #import ipdb; ipdb.set_trace()
    if pattern.endswith('*'):
        # Perform startswith comparison if pattern ends with '*'
        prefix = pattern[:-1]
        return input_string.startswith(prefix)
    else:
        # Perform strict comparison
        return input_string == pattern

def anonymize_audio(input_wav, input_textgrid, output_wav, keywords=[]):
    intervals = get_intervals(input_textgrid)
    # If no keywords are provided, use spaCy to identify personal names
    if not keywords:
        text = " ".join([tup[-1] for tup in intervals])
        keywords = identify_names(text)
        keywords = [word for item in keywords for word in item.split()]
        keywords = list(set(keywords))
        print(f"Identified keywords containing personal information: {keywords}")
    
    anonymized_intervals = []
    # Load audio file
    audio = AudioSegment.from_wav(input_wav)
    # Anonymize intervals
    for xmin, xmax, text in intervals:
        for keyword in keywords:
            if flexible_compare(text.lower(), keyword.lower()):
                print(f"Anonymizing part from {xmin}s to {xmax}s: {text}")
                beep = Sine(1000).to_audio_segment(duration=int((xmax - xmin) * 1000), volume=audio.dBFS)
                audio = audio.overlay(beep, position=int(xmin * 1000), gain_during_overlay=-inf)
                anonymized_intervals.append((xmin, xmax, text))
    # Save anonymized audio
    audio.export(output_wav, format='wav')
    print(f"Anonymized audio saved to: {output_wav}")
    return anonymized_intervals

if __name__ == "__main__":
    # Call example:
    # python anonymize_audio.py GosVL55_vrabe.wav GosVL55_vrabe.TextGrid GosVL55_vrabe-anonymized.wav [
    # python anonymize_audio.py GosVL55_vrabe.wav GosVL55_vrabe.TextGrid GosVL55_vrabe-anonymized.wav
    if len(sys.argv) < 4:
        print("Usage: python anonymize_audio.py input.wav input.TextGrid output.wav keyword1 keyword2 ...")
        sys.exit(1)
    input_wav = sys.argv[1]
    input_textgrid = sys.argv[2]
    output_wav = sys.argv[3]
    keywords = sys.argv[4:]
  
    anonymize_audio(input_wav, input_textgrid, output_wav, keywords)

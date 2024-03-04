import sys
import wave
import contextlib
from pydub import AudioSegment
from textgrid import TextGrid
from numpy import inf

def anonymize_audio(input_wav, input_textgrid, output_wav, keywords):
    # Load TextGrid file and extract time intervals from "strd-wrd-sgmnt" tier
    tg = TextGrid.fromFile(input_textgrid)
    intervals = []
    for interval in tg.getFirst('strd-wrd-sgmnt'):
        intervals.append((interval.minTime, interval.maxTime, interval.mark))

    # Load audio file
    audio = AudioSegment.from_wav(input_wav)

    # Apply silence to specified intervals
    for xmin, xmax, text in intervals:
        for keyword in keywords:
            if keyword in text:
                silence = AudioSegment.silent(duration=int((xmax - xmin) * 1000))
                audio = audio.overlay(silence, position=int(xmin * 1000), gain_during_overlay=-inf)

    # Save anonymized audio
    audio.export(output_wav, format='wav')
    print(f"Anonymized audio saved to: {output_wav}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python anonymize_audio.py input.wav input.TextGrid output.wav keyword1 keyword2 ...")
        sys.exit(1)

    input_wav = sys.argv[1]
    input_textgrid = sys.argv[2]
    output_wav = sys.argv[3]
    keywords = sys.argv[4:]

    anonymize_audio(input_wav, input_textgrid, output_wav, keywords)

import sys
import os
from textgrid import TextGrid, IntervalTier, Interval
from utils_trs import text_from_trs
from utils_tei import text_from_tei
from utils import align_transcription_to_words

def main(input_trs, input_textgrid, output_textgrid):
    # Load transcription
    if os.path.splitext(input_trs)[-1] == ".trs":
        transcription = text_from_trs(input_trs)
    else:
        transcription = text_from_tei(input_trs, False)
        # Remove ellipsis and '-'
        transcription = transcription.replace('...', '')
        transcription = transcription.replace('…', '')
        #transcription = transcription.replace('-', ' ')

    # Load the input TextGrid
    tg = TextGrid.fromFile(input_textgrid)

    strd_wrd_sgmnt = tg.getFirst("strd-wrd-sgmnt")
    strd_wrd_sgmnt = [(interval.minTime, interval.maxTime, interval.mark) for interval in strd_wrd_sgmnt]
    pog_trs = align_transcription_to_words(strd_wrd_sgmnt, transcription)

    # Add new tier
    new_tier = IntervalTier(name="cnvrstl-wrd-sgmnt", minTime=min(t[0] for t in pog_trs), maxTime=max(t[1] for t in pog_trs))
    for start, end, label in pog_trs:
        new_tier.addInterval(Interval(start, end, label))
    index = next((i for i, tier in enumerate(tg.tiers) if tier.name=="conversational-trs"), None)
    tg.tiers.insert(index + 1, new_tier)

    # Save the modified TextGrid
    tg.write(output_textgrid)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_cnvrstl-wrd-sgmnt_tier.py [cnv-transcription.trs] [input.TextGrid] [output.TextGrid]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
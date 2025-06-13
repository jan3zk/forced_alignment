import re
import string
from difflib import SequenceMatcher

def align_transcription_to_words(strd_wrd_sgmnt, transcription):
    """Align a transcription to the intervals returned by forced alignment.

    The function attempts to pair words from ``transcription`` with the
    intervals in ``strd_wrd_sgmnt``.  If the number of words does not match the
    number of intervals, ``SequenceMatcher`` is used to find the best mapping
    between the two sequences.
    """

    # Treat words inside the brackets as single word
    transcription = re.sub(r"\[([^]]+)\]", lambda m: "[" + m.group(1).replace(" ", "_") + "]", transcription)

    # Tokenize the transcription into words and clean them
    words = transcription.split()
    words = [w for w in words if w and not all(c in string.punctuation for c in w)]
    words = [w for w in words if w not in ["-", "+", "–"]]

    # Remove empty or whitespace-only word intervals from FA output
    strd_wrd_sgmnt = [interval for interval in strd_wrd_sgmnt if interval[2].strip()]

    # If the numbers already match, simply zip them together
    if len(words) == len(strd_wrd_sgmnt):
        return [(interval[0], interval[1], word) for interval, word in zip(strd_wrd_sgmnt, words)]

    def _clean(word: str) -> str:
        """Lower-case ``word`` and strip punctuation for comparison."""
        return re.sub(f"[{re.escape(string.punctuation)}]", "", word).lower()

    fa_words = [interval[2] for interval in strd_wrd_sgmnt]
    cleaned_fa = [_clean(w) for w in fa_words]
    cleaned_words = [_clean(w) for w in words]

    sm = SequenceMatcher(None, cleaned_fa, cleaned_words)
    aligned = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for off in range(i2 - i1):
                start, end, _ = strd_wrd_sgmnt[i1 + off]
                aligned.append((start, end, words[j1 + off]))
        elif tag == "replace":
            start = strd_wrd_sgmnt[i1][0]
            end = strd_wrd_sgmnt[i2 - 1][1]
            aligned.append((start, end, " ".join(words[j1:j2])))
        elif tag == "delete":
            # No transcription word for these intervals
            for idx in range(i1, i2):
                aligned.append(strd_wrd_sgmnt[idx])
        elif tag == "insert":
            # Extra words without intervals -> attach to previous segment
            extra = " ".join(words[j1:j2])
            if aligned:
                s, e, prev = aligned[-1]
                aligned[-1] = (s, e, prev + " " + extra)
            else:
                # If at the very beginning attach to the first interval
                start, end, _ = strd_wrd_sgmnt[0]
                aligned.append((start, end, extra))

    return aligned

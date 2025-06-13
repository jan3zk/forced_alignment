import re
import string
import difflib

def align_transcription_to_words(strd_wrd_sgmnt, transcription):
    """Align transcription words with word intervals from forced alignment.

    The function attempts to match the list of ``words`` derived from the
    transcription with the ``strd_wrd_sgmnt`` intervals returned by the forced
    aligner.  When the number of words and intervals differ the function tries to
    align them using :class:`difflib.SequenceMatcher` and falls back to
    heuristics so that each interval receives a label.
    """

    # Treat words inside the brackets as single word
    transcription = re.sub(r"\[([^]]+)\]", lambda m: "[" + m.group(1).replace(" ", "_") + "]", transcription)

    # Tokenize the transcription into words
    words = transcription.split()
    # Remove empty elements and elements containing only punctuation
    words = [w for w in words if w and not all(ch in string.punctuation for ch in w)]
    # Remove elements containing only '–', '+', '-'
    words = [w for w in words if w not in {"-", "+", "–"}]

    # Remove empty or whitespace-only word intervals
    strd_wrd_sgmnt = [interval for interval in strd_wrd_sgmnt if interval[2].strip()]

    fa_words = [interval[2] for interval in strd_wrd_sgmnt]

    matcher = difflib.SequenceMatcher(None, fa_words, words)
    aligned = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in {"equal", "replace"}:
            length = min(i2 - i1, j2 - j1)
            for k in range(length):
                interval = strd_wrd_sgmnt[i1 + k]
                word = words[j1 + k]
                aligned.append((interval[0], interval[1], word))

            # Extra words or intervals inside a replace operation
            if (j2 - j1) > length:
                extra_words = " ".join(words[j1 + length:j2])
                if aligned:
                    s, e, lbl = aligned[-1]
                    aligned[-1] = (s, e, f"{lbl} {extra_words}")
            elif (i2 - i1) > length:
                for x in range(i1 + length, i2):
                    interval = strd_wrd_sgmnt[x]
                    aligned.append((interval[0], interval[1], fa_words[x]))

        elif tag == "delete":
            for idx in range(i1, i2):
                interval = strd_wrd_sgmnt[idx]
                aligned.append((interval[0], interval[1], fa_words[idx]))

        elif tag == "insert":
            extra_words = " ".join(words[j1:j2])
            if aligned:
                s, e, lbl = aligned[-1]
                aligned[-1] = (s, e, f"{lbl} {extra_words}")
            else:
                interval = strd_wrd_sgmnt[0]
                aligned.append((interval[0], interval[1], extra_words))

    return aligned

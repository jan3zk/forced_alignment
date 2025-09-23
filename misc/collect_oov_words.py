#!/usr/bin/env python3
"""
Collect OOV tokens from TEI transcripts.

Usage:
    python collect_oov_words.py TEI_ROOT LEXICON_PATH OUTPUT_PATH
"""

from __future__ import annotations

import argparse
import pathlib
import re
from typing import Set

from utils_tei import text_from_tei


def load_lexicon_words(path: pathlib.Path) -> Set[str]:
    words: Set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if line and not line.startswith("#"):
                words.add(line.split("\t", 1)[0])
    return words


def collect_oovs(tei_root: pathlib.Path, lex_words: Set[str]) -> Set[str]:
    token_re = re.compile(r"[^\s–-]+")
    oovs: Set[str] = set()

    for xml_path in tei_root.rglob("*.xml"):
        try:
            text = text_from_tei(xml_path, True)
        except Exception:
            continue
        text = text.replace("…", "").replace("...", "").lower()
        for tok in token_re.findall(text):
            word = tok.strip(".,!?\"'()[]")
            if word and word not in lex_words:
                oovs.add(word)

    return oovs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tei_root", type=pathlib.Path, help="Root directory containing TEI transcripts")
    parser.add_argument("lexicon", type=pathlib.Path, help="Existing lexicon file (tab-delimited word\\tphones)")
    parser.add_argument("output", type=pathlib.Path, help="Destination for the OOV word list")
    args = parser.parse_args()

    tei_root = args.tei_root.resolve()
    lexicon_path = args.lexicon.resolve()
    output_path = args.output.resolve()

    if not tei_root.exists():
        parser.error(f"TEI root not found: {tei_root}")
    if not lexicon_path.exists():
        parser.error(f"Lexicon file not found: {lexicon_path}")

    lex_words = load_lexicon_words(lexicon_path)
    oovs = collect_oovs(tei_root, lex_words)

    output_path.write_text("\n".join(sorted(oovs)), encoding="utf-8")
    print(f"Wrote {len(oovs)} OOV tokens to {output_path}")


if __name__ == "__main__":
    main()

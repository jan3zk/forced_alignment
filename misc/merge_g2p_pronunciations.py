#!/usr/bin/env python3
"""
Merge pronunciations produced by a G2P model into an existing lexicon.

Usage:
    python merge_g2p_pronunciations.py LEXICON_PATH G2P_DICT_PATH [--output OUTPUT_PATH]

- LEXICON_PATH:     Tab-delimited dictionary you want to extend.
- G2P_DICT_PATH:    Tab- (or space-) delimited file returned by `mfa g2p`.
- OUTPUT_PATH:      Optional destination; if omitted, the lexicon is modified in place.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Set


def load_word_set(path: Path) -> Set[str]:
    words: Set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            words.add(line.split("\t", 1)[0])
    return words


def iter_new_entries(path: Path, existing: Set[str]) -> Iterable[str]:
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                raise ValueError(f"Malformed line in {path}: {raw!r}")
            word, pron = parts
            if word not in existing:
                yield f"{word}\t{pron}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lexicon", type=Path, help="Existing tab-delimited lexicon.")
    parser.add_argument("g2p_pronunciations", type=Path, help="Pronunciations from `mfa g2p`.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional output path; defaults to modifying the lexicon in place.",
    )
    parser.add_argument(
        "--header",
        default="# --- G2P additions ---",
        help="Header line inserted before appended entries (set to '' to skip).",
    )
    args = parser.parse_args()

    lex_path = args.lexicon.resolve()
    g2p_path = args.g2p_pronunciations.resolve()
    out_path = args.output.resolve() if args.output else lex_path

    if not lex_path.exists():
        parser.error(f"Lexicon not found: {lex_path}")
    if not g2p_path.exists():
        parser.error(f"G2P pronunciations not found: {g2p_path}")

    if out_path != lex_path:
        out_path.write_bytes(lex_path.read_bytes())

    existing = load_word_set(out_path)
    new_entries = list(iter_new_entries(g2p_path, existing))

    if not new_entries:
        print("No new pronunciations to append.")
        return

    with out_path.open("a", encoding="utf-8") as handle:
        if args.header:
            handle.write(f"\n{args.header}\n")
        handle.write("\n".join(new_entries) + "\n")

    print(f"Appended {len(new_entries)} pronunciations to {out_path}")


if __name__ == "__main__":
    main()

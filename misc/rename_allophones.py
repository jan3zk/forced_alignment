#!/usr/bin/env python3
"""
Rename allophone phones that use underscores (e.g., d_n, d_l, p_f) by default
into caret-marked variants (e.g., d^n, d^l, p^f) to avoid MFA collapsing them
to base phones on TextGrid export (MFA treats `_` as a special separator).

This is a token-aware transformer for:
 - phoneset files (one phone per line)
 - converted dictionaries (.txt/.dict with phones as space-separated tokens after the last tab)

Default behavior (can be overridden by --map):
  Replace every `_` in phone tokens with `^` (e.g., `d_n`→`d^n`).
  You can provide an explicit JSON mapping with --map to customize specific
  phones (e.g., {"d_n": "dN", "d_l": "dL"}).

Usage examples:
  # Rename phones in phoneset and both converted dict formats
  python misc/rename_allophones.py \
    --phoneset-in data/nrobida/Fonski_vsi/phoneset_fonski_vsi.txt \
    --phoneset-out data/nrobida/Fonski_vsi/phoneset_fonski_vsi_renamed.txt \
    --dict-in data/nrobida/Fonski_vsi/OPTILEX_fonski_vsi_converted.txt \
    --dict-out data/nrobida/Fonski_vsi/OPTILEX_fonski_vsi_converted_renamed.txt \
    --dict-in data/nrobida/Fonski_vsi/OPTILEX_fonski_vsi_converted.dict \
    --dict-out data/nrobida/Fonski_vsi/OPTILEX_fonski_vsi_converted_renamed.dict

  # Custom mapping (JSON string)
  python misc/rename_allophones.py --map '{"d_n":"dN","d_l":"dL"}' ...
"""

import argparse
import json
from pathlib import Path


# Default transformation replaces '_' with '^' in any phone token.
DEFAULT_MAP: dict[str, str] = {}


def load_mapping(map_arg: str | None):
    if not map_arg:
        return DEFAULT_MAP
    try:
        return json.loads(map_arg)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON for --map: {e}")


def _transform_token(token: str, mp: dict[str, str]) -> str:
    # Prefer explicit mapping; fallback to generic underscore→caret replacement
    if token in mp:
        return mp[token]
    if "_" in token:
        return token.replace("_", "^")
    return token


def rename_phoneset(inp: Path, out: Path, mp: dict[str, str]):
    lines = inp.read_text(encoding="utf-8").splitlines()
    out_lines = []
    for ln in lines:
        ph = ln.strip()
        if not ph:
            continue
        out_lines.append(_transform_token(ph, mp))
    out.write_text("\n".join(out_lines) + "\n", encoding="utf-8")


def rename_dict(inp: Path, out: Path, mp: dict[str, str]):
    out_lines = []
    for raw in inp.read_text(encoding="utf-8").splitlines():
        if not raw:
            continue
        # Split once at last tab to preserve any metadata columns in .dict
        if "\t" in raw:
            head, phones_str = raw.rsplit("\t", 1)
            tokens = [_transform_token(t, mp) for t in phones_str.split()]
            out_lines.append(head + "\t" + " ".join(tokens))
        else:
            # Unexpected, but fall back to token-wise replacement
            tokens = [_transform_token(t, mp) for t in raw.split()]
            out_lines.append(" ".join(tokens))
    out.write_text("\n".join(out_lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Rename underscore allophones in phoneset and dictionaries")
    ap.add_argument("--phoneset-in", type=Path, help="Input phoneset file", required=False)
    ap.add_argument("--phoneset-out", type=Path, help="Output phoneset file", required=False)
    ap.add_argument("--dict-in", type=Path, action="append", help="Input converted dict (.txt/.dict)")
    ap.add_argument("--dict-out", type=Path, action="append", help="Output converted dict (.txt/.dict)")
    ap.add_argument("--map", type=str, help="JSON mapping from old->new phone name", required=False)
    args = ap.parse_args()

    mp = load_mapping(args.map)

    if args.phoneset_in and args.phoneset_out:
        rename_phoneset(args.phoneset_in, args.phoneset_out, mp)

    if args.dict_in or args.dict_out:
        if not (args.dict_in and args.dict_out) or len(args.dict_in) != len(args.dict_out):
            raise SystemExit("Provide matching counts of --dict-in and --dict-out")
        for src, dst in zip(args.dict_in, args.dict_out):
            rename_dict(src, dst, mp)

    print("Done.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""extract_dm_labels.py

Extract the *unique* labels that occur in the tier named ``actual-DM-classif``
from one or more Praat TextGrid files **case‑insensitively**.

Any difference in upper/lower case is ignored: a label like ``C-HES`` and
``c-hes`` count as the same function and will appear *once* in the output,
printed in lower‑case.

Usage
-----
Single file:
    python extract_dm_labels.py path/to/file.TextGrid

Multiple files via a glob pattern (quote patterns to keep the shell from expanding):
    python extract_dm_labels.py "path/to/directory/*.TextGrid"

The script prints one label per line, sorted alphabetically and lower‑cased.

Dependencies:
    pip install textgrid

Author: (Your name here)
"""
from __future__ import annotations

import argparse
import sys
import glob
from pathlib import Path

try:
    from textgrid import TextGrid  # type: ignore
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "ERROR: The 'textgrid' library is required. Install with 'pip install textgrid'.\n"
    )
    raise

TIER_NAME = "actual-DM-classif"


def collect_labels(paths: list[str]) -> set[str]:
    """Return a set of *lower‑cased* labels found in *TIER_NAME* across *paths*."""

    labels: set[str] = set()
    for path in paths:
        try:
            tg = TextGrid.fromFile(path)
            dm_tier = tg.getFirst(TIER_NAME)
        except Exception as err:  # pragma: no cover
            sys.stderr.write(f"Skipping '{path}': {err}\n")
            continue

        for iv in dm_tier.intervals:
            mark = iv.mark.strip().lower()  # case‑insensitive handling
            if mark:
                labels.add(mark)
    return labels


def expand_paths(pattern: str) -> list[str]:
    """Resolve *pattern* into a list of TextGrid file paths.

    The *pattern* may be:
    * the path of a single ``.TextGrid`` file,
    * a directory path (will be treated as ``<dir>/*.TextGrid``), or
    * a glob pattern containing wildcards (``*``, ``?``, ``[]``).
    """

    p = Path(pattern)

    # If the pattern is a directory, match every *.TextGrid inside it
    if p.is_dir():
        return sorted(str(x) for x in p.glob("*.TextGrid"))

    # If it contains wildcard characters, let glob handle it
    if any(ch in pattern for ch in "*?["):
        return sorted(glob.glob(pattern))

    # Otherwise assume it's a single file path
    return [pattern]


def parse_args() -> argparse.Namespace:  # pragma: no cover
    parser = argparse.ArgumentParser(
        description=(
            "Extract unique labels (case‑insensitive) from the 'actual-DM-classif' "
            "tier in Praat TextGrid files and print them one per line."
        )
    )
    parser.add_argument(
        "path",
        help=(
            "Path to a .TextGrid file, a directory containing .TextGrid files, "
            "or a quoted glob pattern (e.g. \"corpus/*.TextGrid\")."
        ),
    )
    return parser.parse_args()


def main() -> None:  # pragma: no cover
    args = parse_args()
    paths = expand_paths(args.path)

    if not paths:
        sys.stderr.write("No files matched the given path/pattern.\n")
        sys.exit(1)

    labels = collect_labels(paths)
    for label in sorted(labels):
        print(label)


if __name__ == "__main__":
    main()

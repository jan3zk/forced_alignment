#!/usr/bin/env python3
"""
Restore underscores in selected TextGrid tiers that were previously mapped to carets.

Usage:
    python restore_allophone_underscores.py INPUT [--output OUTPUT] [--suffix SUFFIX]

- INPUT can be a single .TextGrid file or a directory to process recursively.
- OUTPUT (optional) is a file path (if INPUT is a file) or a directory.
- SUFFIX lets you keep the original file and write the restored version beside it.
"""

from __future__ import annotations

import argparse
import pathlib
from typing import Iterable, Sequence

from textgrid import TextGrid

TARGET_TIERS: Sequence[str] = ("phones", "cnvrstl-syllables")


def iter_textgrids(path: pathlib.Path) -> Iterable[pathlib.Path]:
    if path.is_file():
        if path.suffix.lower() == ".textgrid":
            yield path
    else:
        yield from path.rglob("*.TextGrid")


def restore_tier(tg: TextGrid) -> bool:
    changed = False
    for tier_name in TARGET_TIERS:
        tier = next((t for t in tg.tiers if t.name == tier_name), None)
        if not tier:
            continue
        items = getattr(tier, "intervals", getattr(tier, "points", []))
        for item in items:
            new_mark = item.mark.replace("^", "_")
            if new_mark != item.mark:
                item.mark = new_mark
                changed = True
    return changed


def save_textgrid(src: pathlib.Path, dst: pathlib.Path | None) -> None:
    tg = TextGrid.fromFile(str(src))
    changed = restore_tier(tg)
    target = src if dst is None else dst
    if target != src:
        target.parent.mkdir(parents=True, exist_ok=True)
    if changed or target != src:
        tg.write(str(target))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=pathlib.Path, help="TextGrid file or directory to fix")
    parser.add_argument("--output", type=pathlib.Path, help="Destination file or directory")
    parser.add_argument(
        "--suffix",
        default="",
        help="Suffix to append before .TextGrid when modifying in place (default: none)",
    )
    args = parser.parse_args()

    input_path = args.input.resolve()
    output_path = args.output.resolve() if args.output else None

    grids = list(iter_textgrids(input_path))
    if not grids:
        parser.error("No TextGrid files found")

    for src in grids:
        if output_path is None:
            dst = None
            if args.suffix:
                dst = src.with_name(src.stem + args.suffix + src.suffix)
        else:
            if output_path.is_dir() or input_path.is_dir():
                base = input_path if input_path.is_dir() else input_path.parent
                dst = output_path.joinpath(src.relative_to(base))
            else:
                dst = output_path
        save_textgrid(src, dst)


if __name__ == "__main__":
    main()

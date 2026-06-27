#!/usr/bin/env python3
"""
count_lines.py — Count lines of code in .py and .md files.

For each file it reports:
  - Total lines
  - Blank lines
  - Comment lines  (# lines for .py, HTML/markdown comments for .md)
  - Code lines     (total minus blanks and comments)

Run from any directory:
    python count_lines.py            # scans current directory (non-recursive)
    python count_lines.py --recurse  # walks all subdirectories too
"""

import os
import re
import argparse
from pathlib import Path


# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------

def count_python(lines: list[str]) -> dict:
    """Count lines in a .py file, handling inline # and block ''' / \" \"\"."""
    total = len(lines)
    blank = 0
    comment = 0
    in_multiline = False
    multiline_char = None

    for raw in lines:
        stripped = raw.strip()

        if not stripped:
            blank += 1
            continue

        if in_multiline:
            comment += 1
            # Check whether the closing delimiter is on this line
            idx = stripped.find(multiline_char)
            if idx != -1:
                # Closing delimiter found — leave multiline mode
                # (the rest of the line after the delimiter is code, but
                #  we've already counted the whole line as comment; this
                #  is the conventional approach most tools use)
                in_multiline = False
            continue

        # Detect opening of a triple-quoted string used as a block comment.
        # We only treat it as a comment when it's the first non-whitespace
        # token on the line (i.e. a standalone docstring / block comment).
        for delim in ('"""', "'''"):
            if stripped.startswith(delim):
                # Is the closing delimiter also on the same line (and not
                # immediately re-opened — e.g. `"""one liner"""`)?
                rest = stripped[len(delim):]
                if rest.find(delim) != -1:
                    # One-liner: open and close on same line → comment line
                    comment += 1
                else:
                    # Multi-line block opens here
                    in_multiline = True
                    multiline_char = delim
                    comment += 1
                break
        else:
            # Regular single-line comment
            if stripped.startswith('#'):
                comment += 1
            # else: it's a code line (no action needed; we derive it below)

    code = total - blank - comment
    return {"total": total, "blank": blank, "comment": comment, "code": code}


def count_markdown(lines: list[str]) -> dict:
    """Count lines in a .md file.

    Comments: HTML-style <!-- ... --> blocks (can span multiple lines).
    Code blocks (``` fenced) are counted as *code*, not comments.
    """
    total = len(lines)
    blank = 0
    comment = 0
    in_html_comment = False

    for raw in lines:
        stripped = raw.strip()

        if not stripped:
            blank += 1
            continue

        if in_html_comment:
            comment += 1
            if '-->' in stripped:
                in_html_comment = False
            continue

        if '<!--' in stripped:
            comment += 1
            # Check if the comment closes on the same line
            close_idx = stripped.find('-->', stripped.find('<!--') + 4)
            if close_idx == -1:
                in_html_comment = True
            continue

        # Everything else (headings, paragraphs, fenced code, etc.) is "code"

    code = total - blank - comment
    return {"total": total, "blank": blank, "comment": comment, "code": code}


# ---------------------------------------------------------------------------
# File discovery & aggregation
# ---------------------------------------------------------------------------

EXTENSIONS = {'.py': count_python, '.md': count_markdown}


def scan_directory(root: str, recurse: bool) -> list[Path]:
    root_path = Path(root)
    if recurse:
        paths = []
        for ext in EXTENSIONS:
            paths.extend(root_path.rglob(f'*{ext}'))
        return sorted(set(paths))
    else:
        paths = []
        for ext in EXTENSIONS:
            paths.extend(root_path.glob(f'*{ext}'))
        return sorted(set(paths))


def analyse_file(path: Path) -> dict | None:
    counter = EXTENSIONS.get(path.suffix.lower())
    if counter is None:
        return None
    try:
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        stats = counter(lines)
        stats['file'] = str(path)
        stats['type'] = path.suffix.lower()
        return stats
    except Exception as exc:
        print(f"  [WARN] Could not read {path}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

COL_W = 10  # width for numeric columns

def print_header():
    print(
        f"\n{'FILE':<45} {'TYPE':>5} "
        f"{'TOTAL':>{COL_W}} {'BLANK':>{COL_W}} "
        f"{'COMMENT':>{COL_W}} {'CODE':>{COL_W}}"
    )
    print('-' * (45 + 6 + COL_W * 4 + 3))


def print_row(stats: dict):
    fname = stats['file']
    # Truncate very long paths from the left
    if len(fname) > 44:
        fname = '…' + fname[-(43):]
    print(
        f"{fname:<45} {stats['type']:>5} "
        f"{stats['total']:>{COL_W},} {stats['blank']:>{COL_W},} "
        f"{stats['comment']:>{COL_W},} {stats['code']:>{COL_W},}"
    )


def print_summary(totals_by_type: dict, grand: dict):
    print('-' * (45 + 6 + COL_W * 4 + 3))

    for ext, t in sorted(totals_by_type.items()):
        label = f"SUBTOTAL {ext}"
        print(
            f"{label:<50} "
            f"{t['total']:>{COL_W},} {t['blank']:>{COL_W},} "
            f"{t['comment']:>{COL_W},} {t['code']:>{COL_W},}"
        )

    print('=' * (45 + 6 + COL_W * 4 + 3))
    print(
        f"{'GRAND TOTAL':<50} "
        f"{grand['total']:>{COL_W},} {grand['blank']:>{COL_W},} "
        f"{grand['comment']:>{COL_W},} {grand['code']:>{COL_W},}"
    )
    pct_comment = (grand['comment'] / grand['total'] * 100) if grand['total'] else 0
    pct_code    = (grand['code']    / grand['total'] * 100) if grand['total'] else 0
    print(
        f"\n  Code lines    : {grand['code']:,}  ({pct_code:.1f}% of total)\n"
        f"  Comment lines : {grand['comment']:,}  ({pct_comment:.1f}% of total)\n"
        f"  Blank lines   : {grand['blank']:,}\n"
        f"  Total lines   : {grand['total']:,}\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Count lines of code in .py and .md files.'
    )
    parser.add_argument(
        '--recurse', '-r', action='store_true',
        help='Scan subdirectories recursively (default: current dir only)'
    )
    parser.add_argument(
        'directory', nargs='?', default='.',
        help='Directory to scan (default: current directory)'
    )
    args = parser.parse_args()

    scan_root = os.path.abspath(args.directory)
    print(f"\nScanning: {scan_root}"
          f"{'  (recursive)' if args.recurse else '  (top-level only)'}")

    files = scan_directory(scan_root, args.recurse)
    if not files:
        print("  No .py or .md files found.")
        return

    results = []
    for f in files:
        stats = analyse_file(f)
        if stats:
            results.append(stats)

    if not results:
        print("  Could not read any files.")
        return

    # Totals
    totals_by_type: dict[str, dict] = {}
    grand = {"total": 0, "blank": 0, "comment": 0, "code": 0}

    print_header()
    for s in results:
        print_row(s)
        ext = s['type']
        if ext not in totals_by_type:
            totals_by_type[ext] = {"total": 0, "blank": 0, "comment": 0, "code": 0}
        for k in ("total", "blank", "comment", "code"):
            totals_by_type[ext][k] += s[k]
            grand[k] += s[k]

    print_summary(totals_by_type, grand)


if __name__ == '__main__':
    main()
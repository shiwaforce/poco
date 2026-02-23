"""Interactive choice from a list: fzf if available, else numbered menu (multi-column, colored)."""
import os
import shutil
import subprocess
import sys

# ANSI colors for menu (no dependency on ColorPrint log level)
_CYAN = "\033[36m"
_BOLD_CYAN = "\033[1;36m"
_GREEN = "\033[32m"
_BOLD_GREEN = "\033[1;32m"
_YELLOW = "\033[33m"
_BOLD_YELLOW = "\033[1;33m"
_DIM = "\033[2m"
_RESET = "\033[0m"


def _terminal_width(default=80):
    try:
        return os.get_terminal_size().columns
    except OSError:
        pass
    w = os.environ.get("COLUMNS")
    if w and w.isdigit():
        return int(w)
    return default


def _numbered_columns(lines, width=None):
    """Return list of strings, each string is one row of a multi-column numbered menu."""
    if width is None:
        width = _terminal_width()
    if not lines:
        return []
    max_item = max(len(s) for s in lines)
    num_len = len(str(len(lines)))
    # Each cell: " N. " + item (padded)
    col_content = num_len + 3 + max_item
    ncols = max(1, (width + 2) // (col_content + 2))
    nrows = (len(lines) + ncols - 1) // ncols
    rows = []
    for r in range(nrows):
        cells = []
        for c in range(ncols):
            i = r + c * nrows
            if i < len(lines):
                num = i + 1
                cell = "%s%*d. %s%-*s%s" % (_CYAN, num_len, num, _RESET, max_item, lines[i], _RESET)
                cells.append(cell)
            else:
                cells.append(" " * col_content)
        rows.append("  ".join(cells))
    return rows


def choose_one(lines, prompt="Choose: ", title=None):
    """Let the user pick one line from the list. Returns the selected line or None if empty/abort.
    Uses fzf if available, otherwise a numbered menu (multi-column, colored) with input()."""
    if not lines:
        return None
    lines = [s.strip() for s in lines if s and s.strip()]
    if not lines:
        return None
    fzf_path = shutil.which("fzf")
    if fzf_path:
        try:
            result = subprocess.run(
                [fzf_path],
                input="\n".join(lines),
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0 or not result.stdout.strip():
                return None
            return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
    # Fallback: numbered menu, multi-column, colored
    if title:
        print()
        print(_BOLD_GREEN + "  " + title + _RESET)
        print(_DIM + "  " + ("-" * min(len(title) + 2, _terminal_width() - 4)) + _RESET)
    if len(lines) <= 12:
        for i, line in enumerate(lines, 1):
            print("  %s%2d.%s %s" % (_CYAN, i, _RESET, line))
    else:
        for row in _numbered_columns(lines):
            print("  " + row)
    print()
    try:
        raw = input(_BOLD_YELLOW + prompt + _RESET).strip()
        if not raw:
            return None
        idx = int(raw)
        if 1 <= idx <= len(lines):
            return lines[idx - 1]
    except (ValueError, EOFError, KeyboardInterrupt):
        pass
    return None

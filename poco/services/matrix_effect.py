"""
Matrix-style green "rain" effect for terminal.
Shows falling green characters when running poco up / poco down.
Disable with POCO_MATRIX=0.
- Fixed duration: run_matrix_effect(seconds=5) or POCO_MATRIX_SECONDS.
- Until stop: run_matrix_effect_until(stop_event) in a thread; set event when command finishes.
"""
import os
import random
import sys
import time

GREEN = "\033[92m"
GREEN_BRIGHT = "\033[1;92m"
GREEN_DIM = "\033[2;92m"
RED_BRIGHT = "\033[1;91m"
RESET = "\033[0m"
CHARS = "0123456789"


def show_glitch_message(stream):
    """Write 'glitch in the matrix' in red to stream (e.g. TTY)."""
    if stream is None:
        return
    try:
        stream.write(RED_BRIGHT + "  glitch in the matrix" + RESET + "\n")
        stream.flush()
    except (OSError, BrokenPipeError):
        pass


def _matrix_enabled():
    return os.environ.get("POCO_MATRIX", "1").strip().lower() not in ("0", "false", "no")


def _width():
    try:
        return min(140, max(60, os.get_terminal_size().columns - 2))
    except OSError:
        return 100


def _get_stream():
    if sys.stderr.isatty():
        return sys.stderr
    if sys.stdout.isatty():
        return sys.stdout
    return None


def _write_matrix_line(out, width):
    line_parts = []
    for _ in range(width):
        ch = random.choice(CHARS)
        if random.random() < 0.15:
            line_parts.append(GREEN_BRIGHT + ch + RESET)
        else:
            line_parts.append(GREEN_DIM + ch + RESET)
    out.write("  " + "".join(line_parts) + "\n")
    out.flush()


def run_matrix_effect(seconds=None):
    """
    Print Matrix-style green rain for a fixed duration.
    Disable with POCO_MATRIX=0. Duration: POCO_MATRIX_SECONDS (default 5).
    """
    if not _matrix_enabled():
        return
    if seconds is None:
        try:
            seconds = int(os.environ.get("POCO_MATRIX_SECONDS", "5"))
        except ValueError:
            seconds = 5
    seconds = max(1, min(30, seconds))
    out = _get_stream()
    if out is None:
        return
    width = _width()
    end_time = time.time() + seconds
    try:
        out.write(GREEN_BRIGHT + "  " + "".join(random.choice(CHARS) for _ in range(width)) + RESET + "\n")
        out.flush()
        while time.time() < end_time:
            _write_matrix_line(out, width)
            time.sleep(0.035)
        out.write(RESET)
        out.flush()
    except (KeyboardInterrupt, BrokenPipeError, OSError):
        pass


def run_matrix_effect_until(stop_event, stream=None):
    """
    Run matrix rain until stop_event is set.
    stream: if set (e.g. /dev/tty), write there so matrix stays visible when stdout/stderr are redirected.
    """
    if not _matrix_enabled():
        return
    out = stream if stream is not None else _get_stream()
    if out is None:
        return
    try:
        width = _width()
    except OSError:
        width = 80
    try:
        out.write(GREEN_BRIGHT + "  " + "".join(random.choice(CHARS) for _ in range(width)) + RESET + "\n")
        out.flush()
        while not stop_event.is_set():
            _write_matrix_line(out, width)
            stop_event.wait(timeout=0.035)
        out.write(RESET)
        out.flush()
    except (KeyboardInterrupt, BrokenPipeError, OSError):
        pass

"""
Matrix-style green "rain" effect for terminal.
Shows falling green characters when running poco up / poco down.
Disable with POCO_MATRIX=0 or use poco -VV / poco --no-matrix up (or down).
- Fixed height: max 20 lines, updated in place (no terminal scroll).
- Width adapts to terminal size; full lines only, no half-filled rows.
- Fixed duration: run_matrix_effect(seconds=5) or POCO_MATRIX_SECONDS.
- Until stop: run_matrix_effect_until(stop_event) in a thread; set event when command finishes.
"""
import os
import random
import sys
import time

MAX_LINES = 20

GREEN = "\033[92m"
GREEN_BRIGHT = "\033[1;92m"
GREEN_DIM = "\033[2;92m"
RED_BRIGHT = "\033[1;91m"
RESET = "\033[0m"
CHARS = "0123456789"
CURSOR_UP = "\033[%dA"
ERASE_LINE = "\033[K"


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


def _width(stream=None):
    """Terminal content width: full row minus margin. Uses stream's fd when given (e.g. /dev/tty) so size matches the real terminal."""
    try:
        if stream is not None and hasattr(stream, "fileno"):
            try:
                cols = os.get_terminal_size(stream.fileno()).columns
            except (OSError, AttributeError):
                cols = os.get_terminal_size().columns
        else:
            cols = os.get_terminal_size().columns
        return max(10, cols - 2)
    except OSError:
        return 80


def _get_stream():
    if sys.stderr.isatty():
        return sys.stderr
    if sys.stdout.isatty():
        return sys.stdout
    return None


def _generate_line(width):
    """One line of matrix rain: exactly `width` visible characters."""
    parts = []
    for _ in range(width):
        ch = random.choice(CHARS)
        if random.random() < 0.15:
            parts.append(GREEN_BRIGHT + ch + RESET)
        else:
            parts.append(GREEN_DIM + ch + RESET)
    return "".join(parts)


def _draw_lines(out, lines, prefix="  "):
    for line in lines:
        out.write(ERASE_LINE + prefix + line + "\n")
    out.flush()


def run_matrix_effect(seconds=None):
    """
    Print Matrix-style green rain for a fixed duration (max 20 lines, in-place).
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
    end_time = time.time() + seconds
    try:
        width = _width(stream=out)
        buffer = [_generate_line(width) for _ in range(MAX_LINES)]
        _draw_lines(out, buffer)
        while time.time() < end_time:
            time.sleep(0.035)
            width = _width(stream=out)
            buffer = buffer[1:] + [_generate_line(width)]
            out.write(CURSOR_UP % MAX_LINES)
            _draw_lines(out, buffer)
        out.write(RESET)
        out.flush()
    except (KeyboardInterrupt, BrokenPipeError, OSError):
        pass


def run_matrix_effect_until(stop_event, stream=None):
    """
    Run matrix rain until stop_event is set.
    Max 20 lines, updated in place; width follows terminal size.
    stream: if set (e.g. /dev/tty), write there so matrix stays visible when stdout/stderr are redirected.
    """
    if not _matrix_enabled():
        return
    out = stream if stream is not None else _get_stream()
    if out is None:
        return
    try:
        width = _width(stream=out)
    except OSError:
        width = 80
    try:
        buffer = [_generate_line(width) for _ in range(MAX_LINES)]
        _draw_lines(out, buffer)
        while not stop_event.is_set():
            stop_event.wait(timeout=0.035)
            if stop_event.is_set():
                break
            width = _width(stream=out)
            buffer = buffer[1:] + [_generate_line(width)]
            out.write(CURSOR_UP % MAX_LINES)
            _draw_lines(out, buffer)
        out.write(RESET)
        out.flush()
    except (KeyboardInterrupt, BrokenPipeError, OSError):
        pass

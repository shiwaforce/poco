"""
Matrix-style green "rain" effect for terminal.
Shows falling green characters when running poco up / poco down.
Off until the user enables it (install prompt, first interactive command, or `poco matrix on`).
The choice is stored in ~/.poco/settings.yml. POCO_MATRIX=0/1 overrides that for one process.
poco -VV / poco --no-matrix disables it for one up/down and shows the full log.
- Fixed height: max 20 lines, updated in place (no terminal scroll).
- Width adapts to terminal size; full lines only, no half-filled rows.
- Fixed duration: run_matrix_effect(seconds=5) or POCO_MATRIX_SECONDS.
- Until stop: run_matrix_effect_until(stop_event) in a thread; set event when command finishes.
"""
import os
import random
import sys
import time

from .state import StateHolder
from .yaml_utils import YamlUtils

# Slightly slower refresh on Windows for smoother display (CON/console redraw)
_MATRIX_SLEEP = 0.05 if sys.platform == "win32" else 0.035

MAX_LINES = 20

GREEN = "\033[92m"
GREEN_BRIGHT = "\033[1;92m"
GREEN_DIM = "\033[2;92m"
RED_BRIGHT = "\033[1;91m"
RESET = "\033[0m"
CHARS = "0123456789"
SHIWAFORCE = "SHIWAFORCE"
SHIWAFORCE_CHANCE = 0.008  # % chance per line to show SHIWAFORCE
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


_SKIP_MATRIX_PROMPT_COMMANDS = frozenset({"matrix", "help"})

_MATRIX_PROMPT_BODY = (
    "Enable the poco matrix effect?\n"
    "\n"
    "During poco up and poco down, poco can show a Matrix-style rain\n"
    "and hide the live log. Only the final result is shown.\n"
    "\n"
    "You can change this later with: poco matrix on | poco matrix off"
)


def _settings_path():
    base = StateHolder.home_dir
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".poco")
    return os.path.join(base, "settings.yml")


def _coerce_matrix_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in ("0", "false", "no", "off", "")
    if isinstance(value, (int, float)):
        return value != 0
    return bool(value)


def _env_matrix_override():
    """Return True/False when POCO_MATRIX is set to a non-empty value, else None."""
    env = os.environ.get("POCO_MATRIX")
    if env is None or env.strip() == "":
        return None
    return env.strip().lower() not in ("0", "false", "no")


def matrix_preference():
    """Saved matrix choice: True, False, or None when the user has not answered yet."""
    path = _settings_path()
    if not os.path.exists(path):
        return None
    data = YamlUtils.read(path, fault_tolerant=True)
    if not isinstance(data, dict) or "matrix" not in data or data.get("matrix") is None:
        return None
    return _coerce_matrix_bool(data.get("matrix"))


def save_matrix_preference(enabled):
    """Write matrix: true/false to ~/.poco/settings.yml, keeping any other keys."""
    path = _settings_path()
    base = os.path.dirname(path)
    if base and not os.path.exists(base):
        os.makedirs(base, mode=0o700)
    data = {}
    if os.path.exists(path):
        existing = YamlUtils.read(path, fault_tolerant=True)
        if isinstance(existing, dict):
            data = existing
    data["matrix"] = bool(enabled)
    YamlUtils.write(path, data)


def _matrix_enabled():
    override = _env_matrix_override()
    if override is not None:
        return override
    pref = matrix_preference()
    if pref is None:
        return False
    return pref


def _is_interactive_tty():
    try:
        return bool(sys.stdin.isatty() and sys.stdout.isatty())
    except (AttributeError, ValueError, OSError):
        return False


def should_ask_matrix_preference(command=None):
    """True when an interactive command should ask before it runs."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    if command in _SKIP_MATRIX_PROMPT_COMMANDS:
        return False
    if not _is_interactive_tty():
        return False
    return matrix_preference() is None


def matrix_command_should_ask():
    """True when `poco matrix` with no argument should show the question."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    if not _is_interactive_tty():
        return False
    return matrix_preference() is None


def _boxed(text):
    lines = text.split("\n")
    width = max((len(line) for line in lines), default=0)
    bar = "+" + ("-" * (width + 2)) + "+"
    rows = [bar]
    for line in lines:
        rows.append("| " + line.ljust(width) + " |")
    rows.append(bar)
    return "\n".join(rows)


def ask_matrix_preference():
    """Ask in English whether to enable the matrix effect and save the answer.

    Empty Enter, n, and no save False. y and yes save True.
    Ctrl+C or EOF does not write the file.
    """
    print()
    print(_boxed(_MATRIX_PROMPT_BODY))
    while True:
        try:
            raw = input("Enable it? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            raise SystemExit(130)
        if raw in ("y", "yes"):
            enabled = True
            break
        if raw in ("n", "no", ""):
            enabled = False
            break
        print("Please answer y or n.")
    save_matrix_preference(enabled)
    return enabled


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
    """One line of matrix rain: exactly `width` visible characters.
    Occasionally (~8%) embeds SHIWAFORCE in bright green so it's readable."""
    if width >= len(SHIWAFORCE) and random.random() < SHIWAFORCE_CHANCE:
        pos = random.randint(0, width - len(SHIWAFORCE))
        parts = []
        for i in range(width):
            if pos <= i < pos + len(SHIWAFORCE):
                ch = SHIWAFORCE[i - pos]
                parts.append(GREEN_BRIGHT + ch + RESET)
            else:
                ch = random.choice(CHARS)
                if random.random() < 0.15:
                    parts.append(GREEN_BRIGHT + ch + RESET)
                else:
                    parts.append(GREEN_DIM + ch + RESET)
        return "".join(parts)
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
    try:
        out.flush()
    except (OSError, BrokenPipeError):
        pass


def run_matrix_effect(seconds=None):
    """
    Print Matrix-style green rain for a fixed duration (max 20 lines, in-place).
    Runs only when the effect is enabled. Duration: POCO_MATRIX_SECONDS (default 5).
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
            time.sleep(_MATRIX_SLEEP)
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
            stop_event.wait(timeout=_MATRIX_SLEEP)
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

"""Unit tests for start command output extraction and matrix glitch message."""
from io import StringIO
from unittest.mock import patch

# Import the module-level helper and matrix show_glitch_message
from poco.commands.start import _extract_final_output, _filter_matrix_noise, _get_tty_stream
from poco.services.host_port_checker import PortConflict, print_port_conflict_at_end
from poco.services.matrix_effect import show_glitch_message


def test_extract_final_output_from_up_marker():
    text = "pull...\nbuild...\n[+] up 10/10\n ✔ Container a  Running\nNAME\tIMAGE\n..."
    assert _extract_final_output(text).startswith("[+] up 10/10")
    assert "pull" not in _extract_final_output(text)


def test_extract_final_output_from_down_marker():
    text = "stuff\n[+] down 10/10\n ✔ Container a  Stopped\nNAME\tIMAGE\n..."
    assert _extract_final_output(text).startswith("[+] down 10/10")


def test_extract_final_output_from_name_header():
    text = "no marker\nNAME IMAGE\nsimpl-a   img\n"
    result = _extract_final_output(text)
    assert "NAME IMAGE" in result
    assert "simpl-a" in result


def test_extract_final_output_empty():
    assert _extract_final_output("") == ""
    assert _extract_final_output("   \n  ") == "   \n  "


def test_extract_final_output_fallback_last_60():
    lines = ["line %d" % i for i in range(100)]
    result = _extract_final_output("\n".join(lines))
    assert result.strip().startswith("line 40")
    assert "line 99" in result
    assert "line 0" not in result


def test_filter_matrix_noise_removes_executing_and_dash_lines():
    text = (
        "Executing before_script in alpine:latest image\n"
        " - mkdir -p docker/mnt/shiwa/log\n"
        "[+] up 10/10\n"
        "NAME\tIMAGE\n"
        "simpl-a-1\timg\n"
    )
    out = _filter_matrix_noise(text)
    assert "Executing " not in out
    assert " - mkdir" not in out
    assert "[+] up 10/10" in out
    assert "NAME" in out
    assert "simpl-a-1" in out


def test_filter_matrix_noise_removes_docker_command_lines():
    text = (
        "Docker command: ['docker', 'compose', 'up', '-d']\n"
        "[+] up 10/10\n"
        "NAME\tIMAGE\n"
    )
    out = _filter_matrix_noise(text)
    assert "Docker command:" not in out
    assert "[+] up 10/10" in out
    assert "NAME" in out


def test_show_glitch_message_none_stream():
    show_glitch_message(None)  # must not raise


def test_show_glitch_message_writes_red():
    buf = StringIO()
    show_glitch_message(buf)
    out = buf.getvalue()
    assert "glitch in the matrix" in out
    assert "\033" in out  # ANSI


def test_print_port_conflict_visible_on_tty():
    conflict = PortConflict(
        "Cannot start project \"demo\" with plan \"default\".\n\n"
        "Host port conflicts:\n  Port 80:\n    container: other-proxy-1\n"
    )
    tty = StringIO()
    with patch("poco.services.console_logger.ColorPrint.print_error"):
        print_port_conflict_at_end(conflict, tty_stream=tty)
    assert "Port 80" in tty.getvalue()
    assert "other-proxy-1" in tty.getvalue()


def test_get_tty_stream_never_raises():
    """_get_tty_stream() must not raise; returns None or a stream (with write/flush/close)."""
    stream = _get_tty_stream()
    if stream is not None:
        assert hasattr(stream, "write") and hasattr(stream, "flush")
        stream.close()
    # if None: no TTY available (e.g. CI), which is valid


def test_get_tty_stream_prefers_dev_tty_when_open_succeeds():
    """When open('/dev/tty', 'w') succeeds, that stream is returned (Unix/Git Bash path)."""
    fake_stream = StringIO()

    def open_mock(path, *args, **kwargs):
        return fake_stream

    with patch("builtins.open", side_effect=open_mock):
        with patch("os.ctermid", side_effect=AttributeError):
            stream = _get_tty_stream()
    assert stream is not None
    stream.write("x")
    if hasattr(stream, "close"):
        stream.close()


def test_get_tty_stream_returns_none_when_all_fail():
    """When ctermid fails and /dev/tty and CON all fail to open, returns None."""
    def open_raise(*args, **kwargs):
        raise OSError("nope")
    with patch("builtins.open", side_effect=open_raise):
        stream = _get_tty_stream()
    assert stream is None


def test_get_tty_stream_windows_tries_con():
    """On Windows, when /dev/tty fails, we try open('CON')."""
    call_paths = []
    def open_track(path, *args, **kwargs):
        call_paths.append(path)
        if path == "CON":
            return StringIO()  # pretend CON works
        raise OSError("no tty")
    with patch("builtins.open", side_effect=open_track):
        with patch("sys.platform", "win32"):
            with patch("os.ctermid", side_effect=AttributeError):
                stream = _get_tty_stream()
    assert "CON" in call_paths
    assert stream is not None
    if hasattr(stream, "close"):
        stream.close()

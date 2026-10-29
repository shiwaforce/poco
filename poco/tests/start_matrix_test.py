"""Unit tests for start command output extraction and matrix glitch message."""
import os
from io import StringIO
from unittest.mock import patch

import pytest

# Import the module-level helper and matrix show_glitch_message
from poco.commands.matrix import Matrix
from poco.commands.start import _extract_final_output, _filter_matrix_noise, _get_tty_stream
from poco.services.host_port_checker import PortConflict, print_port_conflict_at_end
from poco.services.matrix_effect import (
    _matrix_enabled,
    ask_matrix_preference,
    matrix_command_should_ask,
    matrix_preference,
    save_matrix_preference,
    should_ask_matrix_preference,
    show_glitch_message,
)
from poco.services.state import StateHolder


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
        with patch("os.ctermid", side_effect=AttributeError, create=True):
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
            with patch("os.ctermid", side_effect=AttributeError, create=True):
                stream = _get_tty_stream()
    assert "CON" in call_paths
    assert stream is not None
    if hasattr(stream, "close"):
        stream.close()


def _use_home(monkeypatch, tmp_path):
    monkeypatch.setattr(StateHolder, "home_dir", str(tmp_path))
    monkeypatch.delenv("POCO_MATRIX", raising=False)


def test_matrix_disabled_without_env_or_file(tmp_path, monkeypatch):
    _use_home(monkeypatch, tmp_path)
    assert matrix_preference() is None
    assert _matrix_enabled() is False


def test_matrix_file_true_without_env(tmp_path, monkeypatch):
    _use_home(monkeypatch, tmp_path)
    save_matrix_preference(True)
    assert matrix_preference() is True
    assert _matrix_enabled() is True


def test_matrix_env_overrides_file(tmp_path, monkeypatch):
    _use_home(monkeypatch, tmp_path)
    save_matrix_preference(False)
    monkeypatch.setenv("POCO_MATRIX", "1")
    assert _matrix_enabled() is True
    save_matrix_preference(True)
    monkeypatch.setenv("POCO_MATRIX", "0")
    assert _matrix_enabled() is False
    monkeypatch.setenv("POCO_MATRIX", "false")
    assert _matrix_enabled() is False
    monkeypatch.setenv("POCO_MATRIX", "no")
    assert _matrix_enabled() is False


def test_matrix_save_keeps_other_settings(tmp_path, monkeypatch):
    _use_home(monkeypatch, tmp_path)
    settings = tmp_path / "settings.yml"
    settings.write_text("other: keep\n", encoding="utf-8")
    save_matrix_preference(True)
    text = settings.read_text(encoding="utf-8")
    assert "other: keep" in text
    assert "matrix: true" in text


def test_ask_matrix_preference_yes_no_enter(tmp_path, monkeypatch, capsys):
    _use_home(monkeypatch, tmp_path)
    monkeypatch.setattr("builtins.input", lambda prompt="": "y")
    assert ask_matrix_preference() is True
    assert matrix_preference() is True
    assert "Enable the poco matrix effect?" in capsys.readouterr().out

    monkeypatch.setattr("builtins.input", lambda prompt="": "n")
    assert ask_matrix_preference() is False
    assert matrix_preference() is False

    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    assert ask_matrix_preference() is False
    assert matrix_preference() is False

    monkeypatch.setattr("builtins.input", lambda prompt="": "yes")
    assert ask_matrix_preference() is True
    assert matrix_preference() is True


def test_ask_matrix_preference_interrupt_does_not_save(tmp_path, monkeypatch):
    _use_home(monkeypatch, tmp_path)

    def _interrupt(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", _interrupt)
    with pytest.raises(SystemExit) as caught:
        ask_matrix_preference()
    assert caught.value.code == 130
    assert matrix_preference() is None
    assert not (tmp_path / "settings.yml").exists()


def test_should_ask_false_during_pytest_or_without_tty(tmp_path, monkeypatch):
    _use_home(monkeypatch, tmp_path)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "test_should_ask")
    monkeypatch.setattr("poco.services.matrix_effect._is_interactive_tty", lambda: True)
    assert should_ask_matrix_preference("up") is False
    assert matrix_command_should_ask() is False

    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr("poco.services.matrix_effect._is_interactive_tty", lambda: False)
    assert should_ask_matrix_preference("up") is False
    assert matrix_command_should_ask() is False


def test_should_ask_true_only_for_interactive_commands(tmp_path, monkeypatch):
    _use_home(monkeypatch, tmp_path)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr("poco.services.matrix_effect._is_interactive_tty", lambda: True)
    assert should_ask_matrix_preference("up") is True
    assert should_ask_matrix_preference(None) is True
    assert should_ask_matrix_preference("matrix") is False
    assert should_ask_matrix_preference("help") is False
    assert matrix_command_should_ask() is True
    save_matrix_preference(False)
    assert should_ask_matrix_preference("up") is False
    assert matrix_command_should_ask() is False


def test_matrix_command_on_off_and_status(tmp_path, monkeypatch, capsys):
    _use_home(monkeypatch, tmp_path)
    StateHolder.args = {"<state>": "on"}
    Matrix().execute()
    assert matrix_preference() is True
    assert "Matrix effect is on." in capsys.readouterr().out

    StateHolder.args = {"<state>": "off"}
    Matrix().execute()
    assert matrix_preference() is False
    out = capsys.readouterr().out
    assert "Matrix effect is off." in out

    StateHolder.args = {"<state>": None}
    monkeypatch.setattr("poco.services.matrix_effect._is_interactive_tty", lambda: False)
    Matrix().execute()
    assert "Turn it on with: poco matrix on" in capsys.readouterr().out

    StateHolder.args = {"<state>": "maybe"}
    with pytest.raises(SystemExit):
        Matrix().execute()


def test_matrix_command_asks_when_unset(tmp_path, monkeypatch):
    _use_home(monkeypatch, tmp_path)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr("poco.services.matrix_effect._is_interactive_tty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda prompt="": "n")
    StateHolder.args = {"<state>": None}
    Matrix().execute()
    assert matrix_preference() is False


@patch("poco.services.environment_utils.EnvironmentUtils.check_version")
def test_poco_matrix_on_saves_preference(check_version, tmp_path, monkeypatch):
    monkeypatch.delenv("POCO_MATRIX", raising=False)
    StateHolder.offline = False
    from poco.poco import Poco

    Poco(home_dir=str(tmp_path), argv=["matrix", "on"]).start_flow()
    assert matrix_preference() is True
    check_version.assert_called()


def test_supported_python_notice_is_3_14_10():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    for rel in ("poco/poco.py", "README.md"):
        with open(os.path.join(root, rel), encoding="utf-8") as handle:
            text = handle.read()
        assert "3.14.10" in text
        assert "3.14.3" not in text

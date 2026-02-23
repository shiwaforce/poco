"""Unit tests for start command output extraction and matrix glitch message."""
from io import StringIO

# Import the module-level helper and matrix show_glitch_message
from poco.commands.start import _extract_final_output
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


def test_show_glitch_message_none_stream():
    show_glitch_message(None)  # must not raise


def test_show_glitch_message_writes_red():
    buf = StringIO()
    show_glitch_message(buf)
    out = buf.getvalue()
    assert "glitch in the matrix" in out
    assert "\033" in out  # ANSI

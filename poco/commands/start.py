import os
import sys
import threading
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.command_handler import CommandHandler
from ..services.console_logger import ColorPrint
from ..services.matrix_effect import run_matrix_effect_until
from ..services.matrix_effect import _matrix_enabled
from ..services.matrix_effect import show_glitch_message


def _extract_final_output(text):
    """Keep only the final block: [+] up/down N/N and the container table."""
    if not text or not text.strip():
        return text
    markers = ["[+] up ", "[+] down "]
    start = -1
    for m in markers:
        idx = text.rfind(m)
        if idx != -1 and (start == -1 or idx < start):
            start = idx
    if start == -1:
        idx = text.rfind("\nNAME ")
        if idx != -1:
            start = idx + 1
    if start >= 0:
        return text[start:]
    lines = text.split("\n")
    return "\n".join(lines[-60:]) if len(lines) > 60 else text


class Start(AbstractCommand):

    command = ["start", "up"]
    args = ["[<project/plan>]"]
    args_descriptions = {"[<project/plan>]": "Name of the project in the catalog and/or name of the project's plan"}
    description = "Run: 'poco start nginx/default' or 'poco up nginx/default' to start nginx project (docker, helm " \
                  "or kubernetes) with the default plan."

    run_command = "start"
    need_checkout = True

    def prepare_states(self):
        StateUtils.calculate_name_and_work_dir()
        StateUtils.prepare("compose_handler")

    def resolve_dependencies(self):

        if StateHolder.catalog_element is not None and not StateUtils.check_variable('repository'):
            ColorPrint.exit_after_print_messages(message="Repository not found for: " + str(StateHolder.name))
        self.check_poco_file()

    def execute(self):
        use_matrix_capture = (
            self.run_command in ("start", "stop") and _matrix_enabled()
        )
        tty_stream = None
        pipe_r = pipe_w = None
        saved_stdout = saved_stderr = None

        if use_matrix_capture:
            try:
                tty_stream = open(os.ctermid() if hasattr(os, "ctermid") else "/dev/tty", "w")
            except (OSError, AttributeError):
                use_matrix_capture = False

        if use_matrix_capture and tty_stream:
            pipe_r, pipe_w = os.pipe()
            saved_stdout = os.dup(1)
            saved_stderr = os.dup(2)
            os.dup2(pipe_w, 1)
            os.dup2(pipe_w, 2)
            stop_matrix = threading.Event()
            matrix_thread = threading.Thread(
                target=run_matrix_effect_until,
                args=(stop_matrix,),
                kwargs={"stream": tty_stream},
                daemon=True,
            )
            matrix_thread.start()
        else:
            stop_matrix = None
            matrix_thread = None

        failed = False
        try:
            if self.need_checkout:
                StateHolder.compose_handler.run_checkouts()
            CommandHandler().run(self.run_command)
            if hasattr(self, "end_message"):
                ColorPrint.print_info(getattr(self, "end_message"))
        except Exception:
            failed = True
            raise
        finally:
            if matrix_thread is not None and stop_matrix is not None:
                stop_matrix.set()
                matrix_thread.join(timeout=1.0)
            if pipe_w is not None:
                os.dup2(saved_stdout, 1)
                os.dup2(saved_stderr, 2)
                os.close(pipe_w)
                os.close(saved_stdout)
                os.close(saved_stderr)
                data = b""
                while True:
                    try:
                        chunk = os.read(pipe_r, 4096)
                    except OSError:
                        break
                    if not chunk:
                        break
                    data += chunk
                os.close(pipe_r)
                try:
                    text = data.decode("utf-8", errors="replace")
                    if failed and tty_stream is not None:
                        show_glitch_message(tty_stream)
                    if failed:
                        if text:
                            sys.stdout.write(text)
                            if not text.endswith("\n"):
                                sys.stdout.write("\n")
                            sys.stdout.flush()
                    else:
                        tail = _extract_final_output(text)
                        if tail:
                            sys.stdout.write(tail)
                            if not tail.endswith("\n"):
                                sys.stdout.write("\n")
                            sys.stdout.flush()
                except Exception:
                    pass
            if tty_stream is not None and tty_stream not in (sys.stdout, sys.stderr):
                try:
                    tty_stream.close()
                except OSError:
                    pass

    @staticmethod
    def check_poco_file():
        if not StateUtils.check_variable('poco_file'):
            poco_file = str(StateHolder.repository.target_dir if StateHolder.repository is not None
                            else os.getcwd()) + '/poco.yml'
            ColorPrint.print_error(message="Poco file not found: " + poco_file)
            ColorPrint.exit_after_print_messages(message="Use 'poco init " + StateHolder.name +
                                                         "', that will generate a default poco file for you",
                                                 msg_type="warn")

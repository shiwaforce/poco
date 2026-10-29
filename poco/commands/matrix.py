"""Enable or disable the matrix effect shown during poco up / poco down."""
import os

from .abstract_command import AbstractCommand
from ..services.console_logger import ColorPrint
from ..services.state import StateHolder
from ..services.state_utils import StateUtils
from ..services import matrix_effect


class Matrix(AbstractCommand):

    command = "matrix"
    args = ["[<state>]"]
    args_descriptions = {
        "[<state>]": "on or off. Omit to choose interactively when not set yet, or to print the current state.",
    }
    description = "Run: 'poco matrix on' or 'poco matrix off' to enable or disable the matrix effect. " \
                  "'poco matrix' asks on a terminal when no choice is saved yet."

    def prepare_states(self):
        StateUtils.prepare("config")

    def resolve_dependencies(self):
        pass

    def execute(self):
        state = StateHolder.args.get("<state>")
        if state is None:
            state = ""
        state = str(state).strip().lower()
        if state in ("on", "off"):
            matrix_effect.save_matrix_preference(state == "on")
            ColorPrint.print_with_lvl(message="Matrix effect is %s." % state, lvl=-1)
            return
        if state:
            ColorPrint.exit_after_print_messages(
                message="Unknown matrix state %r. Use: poco matrix on | poco matrix off" % state
            )
        if matrix_effect.matrix_command_should_ask():
            matrix_effect.ask_matrix_preference()
            return
        pref = matrix_effect.matrix_preference()
        if pref is None:
            ColorPrint.print_with_lvl(
                message="Matrix effect is off. Enable with: poco matrix on",
                lvl=-1,
            )
            return
        if pref:
            ColorPrint.print_with_lvl(
                message="Matrix effect is on. Turn it off with: poco matrix off",
                lvl=-1,
            )
        else:
            ColorPrint.print_with_lvl(
                message="Matrix effect is off. Turn it on with: poco matrix on",
                lvl=-1,
            )
        if os.environ.get("POCO_MATRIX", "").strip():
            ColorPrint.print_with_lvl(
                message="POCO_MATRIX is set and overrides the saved choice for this process.",
                lvl=-1,
            )

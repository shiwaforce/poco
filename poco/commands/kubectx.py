"""List or switch kubectl context (kubectx-style)."""
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint
from ..services.environment_utils import EnvironmentUtils
from ..services.interactive import choose_one
import subprocess
import sys


class Kubectx(AbstractCommand):

    command = "kubectx"
    args = ["[<context>]", "[-i]", "[--choose]"]
    args_descriptions = {
        "[<context>]": "Context name to switch to. Omit to list contexts.",
        "[-i]": "Interactive: choose context from menu/fzf.",
        "[--choose]": "Same as -i.",
    }
    description = "Run: 'poco kubectx' to list contexts, 'poco kubectx <context>' to switch. Use -i to choose interactively."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        EnvironmentUtils.check_kubernetes()

    def execute(self):
        context = StateHolder.args.get("<context>")
        interactive = StateHolder.args.get("-i") or StateHolder.args.get("--choose")
        if not context and interactive:
            rc = subprocess.run(
                ["kubectl", "config", "get-contexts", "-o", "name"],
                capture_output=True,
                text=True,
                shell=False,
            )
            if rc.returncode != 0 or not rc.stdout.strip():
                ColorPrint.exit_after_print_messages(message="No contexts or kubectl failed.")
            lines = [s.strip() for s in rc.stdout.strip().splitlines() if s.strip()]
            context = choose_one(lines, prompt="Context number: ")
            if not context:
                return
        if context:
            rc = subprocess.run(
                ["kubectl", "config", "use-context", context],
                shell=False,
            )
            if rc.returncode != 0:
                ColorPrint.exit_after_print_messages(message="Failed to switch context: " + context)
            ColorPrint.print_info("Switched to context: " + context)
        else:
            rc = subprocess.run(
                ["kubectl", "config", "get-contexts"],
                shell=False,
            )
            sys.exit(rc.returncode)

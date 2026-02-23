"""List or switch kubectl context (kubectx-style)."""
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint
from ..services.environment_utils import EnvironmentUtils
import subprocess
import sys


class Kubectx(AbstractCommand):

    command = "kubectx"
    args = ["[<context>]"]
    args_descriptions = {"[<context>]": "Context name to switch to. Omit to list contexts."}
    description = "Run: 'poco kubectx' to list kubectl contexts, 'poco kubectx <context>' to switch context."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        EnvironmentUtils.check_kubernetes()

    def execute(self):
        context = StateHolder.args.get("<context>")
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

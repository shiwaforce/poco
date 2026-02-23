"""List or switch kubectl namespace (kubens-style)."""
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint
from ..services.environment_utils import EnvironmentUtils
from ..services.interactive import choose_one
import subprocess
import sys


class Kubens(AbstractCommand):

    command = "kubens"
    args = ["[<namespace>]", "[-i]", "[--choose]"]
    args_descriptions = {
        "[<namespace>]": "Namespace to switch to. Omit to list namespaces.",
        "[-i]": "Interactive: choose namespace from menu/fzf.",
        "[--choose]": "Same as -i.",
    }
    description = "Run: 'poco kubens' to list namespaces, 'poco kubens <namespace>' to set. Use -i to choose interactively."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        EnvironmentUtils.check_kubernetes()

    def execute(self):
        namespace = StateHolder.args.get("<namespace>")
        interactive = StateHolder.args.get("-i") or StateHolder.args.get("--choose")
        if not namespace and interactive:
            rc = subprocess.run(
                ["kubectl", "get", "namespaces", "-o", "name"],
                capture_output=True,
                text=True,
                shell=False,
            )
            if rc.returncode != 0 or not rc.stdout.strip():
                ColorPrint.exit_after_print_messages(message="No namespaces or kubectl failed.")
            # -o name gives "namespace/foo", we need "foo"
            lines = []
            for s in rc.stdout.strip().splitlines():
                s = s.strip()
                if s.startswith("namespace/"):
                    lines.append(s.split("/", 1)[1])
                elif s:
                    lines.append(s)
            namespace = choose_one(lines, prompt="Namespace number: ")
            if not namespace:
                return
        if namespace:
            rc = subprocess.run(
                ["kubectl", "config", "set-context", "--current", "--namespace=" + namespace],
                shell=False,
            )
            if rc.returncode != 0:
                ColorPrint.exit_after_print_messages(message="Failed to set namespace: " + namespace)
            ColorPrint.print_info("Switched to namespace: " + namespace)
        else:
            rc = subprocess.run(
                ["kubectl", "get", "namespaces"],
                shell=False,
            )
            sys.exit(rc.returncode)

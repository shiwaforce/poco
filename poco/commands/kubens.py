"""List or switch kubectl namespace (kubens-style)."""
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint
from ..services.environment_utils import EnvironmentUtils
import subprocess
import sys


class Kubens(AbstractCommand):

    command = "kubens"
    args = ["[<namespace>]"]
    args_descriptions = {"[<namespace>]": "Namespace to switch to. Omit to list namespaces."}
    description = "Run: 'poco kubens' to list namespaces, 'poco kubens <namespace>' to set current context namespace."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        EnvironmentUtils.check_kubernetes()

    def execute(self):
        namespace = StateHolder.args.get("<namespace>")
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

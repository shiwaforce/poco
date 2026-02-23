"""List Helm releases."""
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.environment_utils import EnvironmentUtils
from ..services.console_logger import ColorPrint
from ..services.interactive import choose_one
import subprocess
import sys


class HelmList(AbstractCommand):

    command = "helm-list"
    args = ["[--all-namespaces]", "[-i]", "[--choose]"]
    args_descriptions = {
        "[--all-namespaces]": "List releases across all namespaces (-A).",
        "[-i]": "Interactive: choose a release (then show helm status).",
        "[--choose]": "Same as -i.",
    }
    description = "Run: 'poco helm-list' to list releases. Use -i to pick one and show status."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        EnvironmentUtils.check_helm()

    def execute(self):
        interactive = StateHolder.args.get("-i") or StateHolder.args.get("--choose")
        if interactive:
            cmd = ["helm", "list", "-q"]
            if StateHolder.args.get("--all-namespaces"):
                cmd.append("-A")
            rc = subprocess.run(cmd, capture_output=True, text=True, shell=False)
            if rc.returncode != 0 or not rc.stdout.strip():
                ColorPrint.print_info("No Helm releases.")
                return
            lines = [s.strip() for s in rc.stdout.strip().splitlines() if s.strip()]
            release = choose_one(lines, prompt="Release number: ")
            if not release:
                return
            rc = subprocess.run(["helm", "status", release], shell=False)
            sys.exit(rc.returncode)
        cmd = ["helm", "list"]
        if StateHolder.args.get("--all-namespaces"):
            cmd.append("-A")
        rc = subprocess.run(cmd, shell=False)
        sys.exit(rc.returncode)

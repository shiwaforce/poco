"""List Helm releases."""
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.environment_utils import EnvironmentUtils
import subprocess
import sys


class HelmList(AbstractCommand):

    command = "helm-list"
    args = ["[--all-namespaces]"]
    args_descriptions = {"[--all-namespaces]": "List releases across all namespaces (-A)."}
    description = "Run: 'poco helm-list' to list Helm releases in current namespace, 'poco helm-list --all-namespaces' for all."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        EnvironmentUtils.check_helm()

    def execute(self):
        cmd = ["helm", "list"]
        if StateHolder.args.get("--all-namespaces"):
            cmd.append("-A")
        rc = subprocess.run(cmd, shell=False)
        sys.exit(rc.returncode)

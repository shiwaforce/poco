"""Run kubectl get for common resources (pods, ns, svc, deploy, etc.)."""
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint
from ..services.environment_utils import EnvironmentUtils
import subprocess
import sys


class KubeGet(AbstractCommand):

    command = "kube-get"
    args = ["<resource>", "[<name>]", "[-n <namespace>]", "[-A]"]
    args_descriptions = {
        "<resource>": "Resource type (e.g. pods, ns, svc, deploy).",
        "[<name>]": "Optional resource name.",
        "[-n <namespace>]": "Namespace (optional).",
        "[-A]": "All namespaces (optional).",
    }
    description = "Run: 'poco kube-get <resource> [name]' to run kubectl get. Use -n <namespace> or -A for all namespaces."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        EnvironmentUtils.check_kubernetes()

    def execute(self):
        resource = StateHolder.args.get("<resource>")
        if not resource:
            ColorPrint.exit_after_print_messages(message="Resource required. E.g. poco kube-get pods, poco kube-get ns")
        name = StateHolder.args.get("<name>")
        namespace = StateHolder.args.get("<namespace>")
        all_ns = StateHolder.args.get("-A")
        cmd = ["kubectl", "get", resource]
        if name:
            cmd.append(name)
        if all_ns:
            cmd.append("-A")
        elif namespace:
            cmd.extend(["-n", namespace])
        rc = subprocess.run(cmd, shell=False)
        sys.exit(rc.returncode)

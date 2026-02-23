"""List Helm repositories."""
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.environment_utils import EnvironmentUtils
import subprocess
import sys


class HelmRepos(AbstractCommand):

    command = "helm-repos"
    args = []
    args_descriptions = {}
    description = "Run: 'poco helm-repos' to list Helm repositories (helm repo list)."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        EnvironmentUtils.check_helm()

    def execute(self):
        rc = subprocess.run(
            ["helm", "repo", "list"],
            shell=False,
        )
        sys.exit(rc.returncode)

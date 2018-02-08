from .abstract_command import AbstractCommand
from ..services.config_handler import ConfigHandler
from ..services.state_utils import StateUtils


class RepoAdd(AbstractCommand):

    sub_command = "repo"
    command = ["add", "modify"]
    args = ["<name>", "<git-url>", "[<branch>]", "[<file>]"]
    args_descriptions = {"<name>": "Name of the repository.",
                         "<git-url>": "URL of catalog's GIT repository",
                         "[<branch>]": "Name of the branch that should be checked out.(default: master)",
                         "[<file>]": "Name of the catalog file in the repository.(default: pocok-catalog.yml)"}
    description = "Add new/Modify repository to the config."

    def prepare_states(self):
        StateUtils.prepare(["config", "catalog"])
        self.prepared_states = True

    def resolve_dependencies(self):
        self.resolved_dependencies = True

    def execute(self):
        ConfigHandler.add()
        self.executed = True

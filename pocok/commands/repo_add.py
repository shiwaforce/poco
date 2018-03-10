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
    description = "Run: 'pocok repo add default https://github.com/shiwaforce/poco-example master' to add new " \
                  "catalog to the config from github and use master branch. Modify command use same metholody."

    def prepare_states(self):
        StateUtils.prepare("catalog")

    def resolve_dependencies(self):
        pass

    def execute(self):
        ConfigHandler.add()

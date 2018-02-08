from .abstract_command import AbstractCommand
from ..services.config_handler import ConfigHandler
from ..services.console_logger import ColorPrint
from ..services.state import StateHolder
from ..services.state_utils import StateUtils


class RepoBranch(AbstractCommand):

    sub_command = "repo"
    command = "branch"
    args = ["<branch>", "[<name>]", "[-f]"]
    args_descriptions = {"<branch>": "Name of the branch that should be checked out.",
                         "[<name>]": "Name of the catalog.",
                         "[-f]": "Force switch."}
    description = "Switch catalog branch if it is using GIT."

    def prepare_states(self):
        StateUtils.prepare(["config", "catalog"])
        self.prepared_states = True

    def resolve_dependencies(self):
        self.resolved_dependencies = True

    def execute(self):
        ConfigHandler.set_branch(StateHolder.args.get('<branch>'), StateHolder.args.get('<name>'))
        ColorPrint.print_info("Branch changed")
        self.executed = True

from .abstract_command import AbstractCommand
from ..services.config_handler import ConfigHandler
from ..services.console_logger import ColorPrint
from ..services.state_utils import StateUtils


class RepoLs(AbstractCommand):

    sub_command = "repo"
    command = "ls"
    description = "Run: 'poco repo ls' to list the configs of repos."

    def prepare_states(self):
        StateUtils.prepare("catalog_read")

    def resolve_dependencies(self):
        pass

    def execute(self):
        ColorPrint.print_info(message=ConfigHandler.print_config())

from .abstract_command import AbstractCommand
from ..services.console_logger import ColorPrint
from ..services.catalog_handler import CatalogHandler
from ..services.state import StateHolder
from ..services.state_utils import StateUtils


class RepoPush(AbstractCommand):

    sub_command = "repo"
    command = "push"
    args = ["[<name>]"]
    args_descriptions = {"[<name>]": "Name of the catalog."}
    description = "Run: 'poco repo push default' to push changes into default catalog's remote GIT repository."

    def prepare_states(self):
        StateUtils.prepare("catalog")

    def resolve_dependencies(self):
        pass

    def execute(self):
        repository = CatalogHandler.get_catalog_repository(StateHolder.args.get('<name>'))
        repository.push()
        ColorPrint.print_info("Push completed")

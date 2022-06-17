from .abstract_command import AbstractCommand
from ..services.catalog_handler import CatalogHandler
from ..services.console_logger import ColorPrint
from ..services.state import StateHolder
from ..services.state_utils import StateUtils


class CatalogUpdate(AbstractCommand):
    command = "catalog-update"
    description = "Run: 'poco repo pull' or 'poco catalog-update' to refresh all catalog information from repository."

    def prepare_states(self):
        StateUtils.prepare("catalog_read")

    def resolve_dependencies(self):
        pass

    def execute(self):
        StateHolder.offline = False
        StateHolder.always_update = True

        CatalogHandler.load()

        ColorPrint.print_info("Pull completed")

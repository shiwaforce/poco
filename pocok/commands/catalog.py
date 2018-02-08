from .abstract_command import AbstractCommand
from ..services.state import StateHolder
from ..services.state_utils import StateUtils
from ..services.console_logger import ColorPrint
from ..services.cta_utils import CTAUtils
from ..services.catalog_handler import CatalogHandler


class Catalog(AbstractCommand):

    command = "catalog"
    description = "List the available projects in repos."

    def prepare_states(self):
        StateUtils.prepare(["config", "catalog"])
        StateHolder.work_dir = StateHolder.base_work_dir
        self.prepared_states = True

    def resolve_dependencies(self):
        if StateHolder.default_catalog_repository is None:
            ColorPrint.print_warning("You have not catalog yet.", lvl=-1)
            ColorPrint.exit_after_print_messages(message=CTAUtils.CTA_STRINGS['default'], msg_type="info")
        self.resolved_dependencies = True

    def execute(self):
        CatalogHandler.print_ls()
        self.executed = True

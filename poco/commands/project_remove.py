from .checkout import Checkout
from ..services.command_handler import CommandHandler
from ..services.console_logger import ColorPrint
from ..services.catalog_handler import CatalogHandler
from ..services.state import StateHolder


class ProjectRemove(Checkout):

    sub_command = "project"
    command = ["remove", "rm"]
    args = ["<name>"]
    args_descriptions = {"<name>": "Name of the project that will be removed"}
    description = "Run: 'poco project remove nginx' or 'poco project rm nginx' to remove 'nginx' " \
                  "project from the catalog."

    def prepare_states(self):
        ProjectRemove.prepare("compose_handler")

    def resolve_dependencies(self):
        self.remove(dry_run=True)

    def execute(self):
        self.remove()
        ColorPrint.print_info("Project removed")

    @staticmethod
    def remove(dry_run=False):

        for catalog in StateHolder.catalogs:
            lst = StateHolder.catalogs[catalog]
            if StateHolder.name in lst:
                ProjectRemove.run(catalog=catalog, lst=lst, dry_run=dry_run)
                return
        if dry_run:
            ColorPrint.exit_after_print_messages(message="Project not exists in catalog: " + StateHolder.name)

    @staticmethod
    def run(catalog, lst, dry_run):
        if not dry_run:
            if StateHolder.poco_file is not None and StateHolder.compose_handler.have_script("remove_script"):
                CommandHandler().run_script("remove_script")
            lst.pop(StateHolder.name)
            CatalogHandler.write_catalog(catalog=catalog)

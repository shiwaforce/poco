from .abstract_command import AbstractCommand
from ..services.state import StateHolder
from ..services.catalog_handler import CatalogHandler
from ..services.state_utils import StateUtils


class RepoBranches(AbstractCommand):

    sub_command = "repo"
    command = "branches"
    args = ["[<name>]"]
    args_descriptions = {"[<name>]": "Name of the catalog."}
    description = "List all available branches of catalog's GIT repository."

    def prepare_states(self):
        StateUtils.prepare(["config", "catalog"])
        self.prepared_states = True

    def resolve_dependencies(self):
        self.resolved_dependencies = True

    def execute(self):
        repository = CatalogHandler.get_catalog_repository(StateHolder.args.get('<name>'))
        repository.print_branches()
        self.executed = True

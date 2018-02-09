from .abstract_command import AbstractCommand
from ..services.config_handler import ConfigHandler
from ..services.state import StateHolder
from ..services.state_utils import StateUtils


class RepoRemove(AbstractCommand):

    sub_command = "repo"
    command = ["remove", "rm"]
    args = ["<name>"]
    args_descriptions = {"<name>": "Name of the repository."}
    description = "Remove repository from local config."

    def prepare_states(self):
        StateHolder.name = StateHolder.args.get('<name>')
        StateUtils.prepare(["config", "catalog_read"])

    def resolve_dependencies(self):
        pass

    def execute(self):
        #if StateHolder.name in StateHolder.catalogs:
            # TODO remove script
            # if self.get_compose_file(silent=True) is not None:
            #    self.init_compose_handler()
            #    CommandHandler(project_utils=self.project_utils).run_script("remove_script")
        #    pass
        ConfigHandler.remove()

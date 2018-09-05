from .abstract_command import AbstractCommand
from ..services.file_utils import FileUtils
from ..services.config_handler import ConfigHandler
from ..services.state import StateHolder
from ..services.state_utils import StateUtils
from ..services.yaml_utils import YamlUtils


class RepoRemove(AbstractCommand):

    sub_command = "repo"
    command = ["remove", "rm"]
    args = ["[<name>]"]
    args_descriptions = {"[<name>]": "Name of the repository."}
    description = "Run: 'poco repo remove default' or 'poco repo rm default' to remove 'default' catalog's config."

    def prepare_states(self):
        StateHolder.name = FileUtils.get_parameter_or_directory_name('<name>')
        StateUtils.prepare("catalog_read")

    def resolve_dependencies(self):
        ConfigHandler.check_name(StateHolder.name)

    def execute(self):
        RepoRemove.remove()

    @staticmethod
    def remove():
        del StateHolder.config[StateHolder.name]
        YamlUtils.write(file=StateHolder.catalog_config_file, data=StateHolder.config)

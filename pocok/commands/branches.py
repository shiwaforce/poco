from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint
from ..services.file_utils import FileUtils


class Branches(AbstractCommand):

    command = "branches"
    args = ["[<name>]"]
    args_descriptions = {"[<name>]": "Name of the project in the catalog."}
    description = "List all available git branches of the project."

    def prepare_states(self):
        StateHolder.name = FileUtils.get_parameter_or_directory_name('<name>')
        StateUtils.prepare("project_repo")

    def resolve_dependencies(self):
        if StateHolder.repository is None:
            ColorPrint.exit_after_print_messages(message="Project not exists " + str(StateHolder.name))

    def execute(self):
        StateHolder.repository.print_branches()

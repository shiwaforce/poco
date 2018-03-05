from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint


class Unpack(AbstractCommand):

    command = "unpack"
    args = ["[<project>]"]
    args_descriptions = {"[<project>]": "Name of the project in the catalog."}
    description = "Unpack archive, install images to local repository."

    def prepare_states(self):
        StateUtils.calculate_name_and_work_dir()
        StateUtils.prepare("project_file")

    def resolve_dependencies(self):
        if StateHolder.poco_file is None:
            ColorPrint.exit_after_print_messages(message="Project not exists " + str(StateHolder.name))

    def execute(self):
        # TODO
        pass


from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint


class Pull(AbstractCommand):

    command = "pull"
    args = ["[<project/plan>]"]
    args_descriptions = {"[<project/plan>]": "Name of the project in the catalog and/or name of the project's plan"}
    description = "Pull all necessary images for the project with the defined or default plan."

    def prepare_states(self):
        StateUtils.calculate_name_and_work_dir()
        StateUtils.prepare("project_file")

    def resolve_dependencies(self):
        if StateHolder.poco_file is None:
            ColorPrint.exit_after_print_messages(message="Project not exists " + str(StateHolder.name))

    def execute(self):
        # TODO
        pass

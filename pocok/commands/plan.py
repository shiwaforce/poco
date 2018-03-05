from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.file_utils import FileUtils
from ..services.console_logger import ColorPrint
from ..services.compose_handler import ComposeHandler


class Plan(AbstractCommand):

    command = "plan"
    args = ["ls", "[<project>]"]
    args_descriptions = {"ls": "List all plan",
                         "[<project>]": "Name of the project in the catalog."}
    description = "Print all available plans of the project."

    def prepare_states(self):
        StateHolder.name = FileUtils.get_parameter_or_directory_name('<project>')
        StateHolder.work_dir = StateHolder.base_work_dir
        StateUtils.prepare("project_file")

    def resolve_dependencies(self):
        if StateHolder.poco_file is None:
            ColorPrint.exit_after_print_messages(message="Project not exists " + str(StateHolder.name))

    def execute(self):
        compose_handler = ComposeHandler(StateHolder.poco_file)
        compose_handler.get_plan_list()

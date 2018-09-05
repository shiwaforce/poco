import os
from .start import Start
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint
from ..services.file_utils import FileUtils
from ..services.compose_handler import ComposeHandler


class Plan(Start):

    command = "plan"
    args = ["ls", "[<name>]"]
    args_descriptions = {"ls": "List all plan",
                         "[<name>]": "Name of the project in the catalog."}
    description = "Run: 'poco plan ls nginx' to print all available plans of the nginx project."

    def prepare_states(self):
        StateHolder.name = FileUtils.get_parameter_or_directory_name('<name>')
        StateHolder.work_dir = StateHolder.base_work_dir
        StateUtils.prepare("project_file")

    def resolve_dependencies(self):
        if not StateUtils.check_variable('repository') and StateHolder.name != FileUtils.get_directory_name():
            ColorPrint.exit_after_print_messages(message="Repository not found for: " + str(StateHolder.name))
        self.check_poco_file()

    def execute(self):
        compose_handler = ComposeHandler(StateHolder.poco_file)
        compose_handler.get_plan_list()


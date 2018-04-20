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
    description = "Run: 'pocok plan ls nginx' to print all available plans of the nginx project."

    def prepare_states(self):
        StateHolder.name = FileUtils.get_parameter_or_directory_name('<name>')
        StateHolder.work_dir = StateHolder.base_work_dir
        StateUtils.prepare("project_file")

    def resolve_dependencies(self):
        if not StateUtils.check_variable('repository') and StateHolder.name != FileUtils.get_directory_name():
            ColorPrint.exit_after_print_messages(message="Repository not found for: " + str(StateHolder.name))
        if not StateUtils.check_variable('poco_file'):
            ColorPrint.print_error(message="Pocok file not found in directory: " +
                                           str(StateHolder.repository.target_dir if StateHolder.repository is not None
                                               else os.getcwd()))
            ColorPrint.exit_after_print_messages(message="Use 'pocok init " + StateHolder.name +
                                             "', that will be generate a default pocok file for you", msg_type="warn")

    def execute(self):
        compose_handler = ComposeHandler(StateHolder.poco_file)
        compose_handler.get_plan_list()

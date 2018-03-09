from .start import Start
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.file_utils import FileUtils
from ..services.compose_handler import ComposeHandler


class Plan(Start):

    command = "plan"
    args = ["ls", "[<project>]"]
    args_descriptions = {"ls": "List all plan",
                         "[<project>]": "Name of the project in the catalog."}
    description = "Print all available plans of the project."

    def prepare_states(self):
        StateHolder.name = FileUtils.get_parameter_or_directory_name('<project>')
        StateHolder.work_dir = StateHolder.base_work_dir
        StateUtils.prepare("project_file")

    def execute(self):
        compose_handler = ComposeHandler(StateHolder.poco_file)
        compose_handler.get_plan_list()

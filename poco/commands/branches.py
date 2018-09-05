from .branch import Branch
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.file_utils import FileUtils


class Branches(Branch):

    command = "branches"
    args = ["[<name>]"]
    args_descriptions = {"[<name>]": "Name of the project in the catalog."}
    description = "Run: 'poco branches nginx' to list all available git branches of the 'nginx' project."

    def prepare_states(self):
        StateHolder.name = FileUtils.get_parameter_or_directory_name('<name>')
        StateHolder.work_dir = StateHolder.base_work_dir
        StateUtils.prepare("project_repo")

    def execute(self):
        StateHolder.repository.print_branches()

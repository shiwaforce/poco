from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint


class Branch(AbstractCommand):

    command = "branch"
    args = ["<name>", "<branch>", "[-f]"]
    args_descriptions = {"<name>": "Name of the project in the catalog.",
                         "<branch>": "Name of the git branch",
                         "-f": "Git force parameter"}
    description = "Run: 'pocok branch nginx master' to switch branch to 'master' on 'nginx' project."

    def prepare_states(self):
        StateUtils.name = StateHolder.args.get('<name>')
        StateUtils.prepare("project_repo")

    def resolve_dependencies(self):
        StateUtils.check_variable('repository')

    def execute(self):
        StateHolder.repository.set_branch(StateHolder.args.get('<branch>'), StateHolder.name,
                                          StateHolder.args.get('-f'))
        ColorPrint.print_info("Branch changed")

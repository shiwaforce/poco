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
    description = "Run: 'poco branch nginx master' to switch branch to 'master' on 'nginx' project."

    def prepare_states(self):
        StateUtils.name = StateHolder.args.get('<name>')
        StateHolder.work_dir = StateHolder.base_work_dir
        StateUtils.prepare("project_repo")

    def resolve_dependencies(self):
        if not StateUtils.check_variable('repository'):
            ColorPrint.exit_after_print_messages(message="Repository not found for: " + str(StateHolder.name))

    def execute(self):
        StateHolder.repository.set_branch(StateHolder.args.get('<branch>'), StateHolder.args.get('-f'))
        ColorPrint.print_info("Branch changed")

from .abstract_command import AbstractCommand
from ..services.console_logger import ColorPrint
from ..services.project_utils import ProjectUtils
from ..services.state_utils import StateUtils
from ..services.state import StateHolder


class Checkout(AbstractCommand):

    command = "checkout"
    args = ["<name>"]
    args_descriptions = {"<name>": "Name of the project"}
    description = "Run: 'pocok checkout nginx' to checkout 'nginx' project from the catalog."

    def prepare_states(self):
        StateHolder.name = StateHolder.args.get('<name>')
        StateHolder.work_dir = StateHolder.base_work_dir
        StateUtils.prepare("catalog")

    def resolve_dependencies(self):
        self.remove(dry_run=True)

    def execute(self):
        self.remove()
        ColorPrint.print_info("Project checkout complete " + StateHolder.repository.target_dir)

    @staticmethod
    def remove(dry_run=False):

        for catalog in StateHolder.catalogs:
            lst = StateHolder.catalogs[catalog]
            if StateHolder.name in lst:
                if not dry_run:
                    StateHolder.repository = \
                        ProjectUtils.get_project_repository(StateHolder.catalogs[catalog].get(StateHolder.name))
                return
        if dry_run:
            ColorPrint.exit_after_print_messages(message="Project not exists in catalog: " + StateHolder.name)

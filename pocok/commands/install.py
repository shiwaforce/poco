from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.environment_utils import EnvironmentUtils
from ..services.console_logger import ColorPrint
from ..services.project_utils import ProjectUtils
from ..services.command_handler import CommandHandler


class Install(AbstractCommand):

    command = "install"
    args = ["[<project/plan>]"]
    args_descriptions = {"[<project/plan>]": "Name of the project in the catalog and/or name of the project's plan"}
    description = "Get projects from remote repository (if its not exists locally yet) and run install scripts."

    def prepare_states(self):
        StateUtils.calculate_name_and_work_dir()
        StateUtils.prepare("compose_handler")

    def resolve_dependencies(self):
        if StateHolder.poco_file is None:
            ColorPrint.exit_after_print_messages(message="Project not exists " + str(StateHolder.name))
        if StateHolder.compose_handler.have_script("init_script"):
            EnvironmentUtils.check_docker()

    def execute(self):
        #  Run init script, if exists
        if StateHolder.compose_handler.have_script("init_script"):
            CommandHandler().run_script("init_script")
        ColorPrint.print_info("Install completed to " + ProjectUtils.get_target_dir(StateHolder.catalog_element))

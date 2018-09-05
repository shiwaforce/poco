from .start import Start
from ..services.state import StateHolder
from ..services.environment_utils import EnvironmentUtils
from ..services.console_logger import ColorPrint
from ..services.project_utils import ProjectUtils
from ..services.command_handler import CommandHandler


class Install(Start):

    command = "install"
    description = "Run: 'poco install nginx/default' to get nginx project from remote repository " \
                  "(if it doesn't exist locally yet) and run install scripts."

    def resolve_dependencies(self):
        Start.resolve_dependencies(self)
        if StateHolder.compose_handler.have_script("init_script"):
            EnvironmentUtils.check_docker()

    def execute(self):
        #  Run init script, if exists
        if StateHolder.compose_handler.have_script("init_script"):
            CommandHandler().run_script("init_script")
        ColorPrint.print_info("Install completed to " + ProjectUtils.get_target_dir(StateHolder.catalog_element))

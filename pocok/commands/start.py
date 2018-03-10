from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.command_handler import CommandHandler
from ..services.console_logger import ColorPrint


class Start(AbstractCommand):

    command = ["start", "up"]
    args = ["[<project/plan>]"]
    args_descriptions = {"[<project/plan>]": "Name of the project in the catalog and/or name of the project's plan"}
    description = "Run: 'pocok start nginx/default' or 'pocok up nginx/default' to start nginx project (docker, helm " \
                  "or kubernetes) with the default plan."

    run_command = "start"
    need_checkout = True

    def prepare_states(self):
        StateUtils.calculate_name_and_work_dir()
        StateUtils.prepare("compose_handler")

    def resolve_dependencies(self):
        StateUtils.check_variable('poco_file')

    def execute(self):
        if self.need_checkout:
            StateHolder.compose_handler.run_checkouts()
        CommandHandler().run(self.run_command)
        if hasattr(self, "end_message"):
            ColorPrint.print_info(getattr(self, "end_message"))

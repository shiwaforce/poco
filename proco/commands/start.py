import os
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.command_handler import CommandHandler
from ..services.console_logger import ColorPrint


class Start(AbstractCommand):

    command = ["start", "up"]
    args = ["[<project/plan>]"]
    args_descriptions = {"[<project/plan>]": "Name of the project in the catalog and/or name of the project's plan"}
    description = "Run: 'proco start nginx/default' or 'proco up nginx/default' to start nginx project (docker, helm " \
                  "or kubernetes) with the default plan."

    run_command = "start"
    need_checkout = True

    def prepare_states(self):
        StateUtils.calculate_name_and_work_dir()
        StateUtils.prepare("compose_handler")

    def resolve_dependencies(self):

        if StateHolder.catalog_element is not None and not StateUtils.check_variable('repository'):
            ColorPrint.exit_after_print_messages(message="Repository not found for: " + str(StateHolder.name))
        self.check_proco_file()

    def execute(self):
        if self.need_checkout:
            StateHolder.compose_handler.run_checkouts()
        CommandHandler().run(self.run_command)
        if hasattr(self, "end_message"):
            ColorPrint.print_info(getattr(self, "end_message"))

    def check_proco_file(self):
        if not StateUtils.check_variable('proco_file'):
            ColorPrint.print_error(message="Proco file not found in directory: " +
                                           str(StateHolder.repository.target_dir if StateHolder.repository is not None
                                               else os.getcwd()))
            ColorPrint.exit_after_print_messages(message="Use 'proco init " + StateHolder.name +
                                                         "', that will be generate a default proco file for you",
                                                 msg_type="warn")

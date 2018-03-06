from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint
from ..services.package_handler import PackageHandler
from ..services.file_utils import FileUtils


class Unpack(AbstractCommand):

    command = "unpack"
    args = ["[<name>]"]
    args_descriptions = {"[<name>]": "Name of the project in the catalog."}
    description = "Unpack archive, install images to local repository."

    def prepare_states(self):
        StateHolder.name = FileUtils.get_parameter_or_directory_name('<name>')
        StateUtils.prepare("compose_handler")

    def resolve_dependencies(self):
        if StateHolder.poco_file is None:
            ColorPrint.exit_after_print_messages(message="Project not exists " + str(StateHolder.name))

    def execute(self):
        PackageHandler().unpack()


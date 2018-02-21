import os
import shutil
from .abstract_command import AbstractCommand
from ..services.console_logger import ColorPrint
from ..services.state_utils import StateUtils
from ..services.file_utils import FileUtils
from ..services.project_utils import ProjectUtils
from ..services.state import StateHolder


class ProjectInit(AbstractCommand):

    command = "init"
    args = ["[<name>]"]
    args_descriptions = {"[<name>]": "Name of the project or the actual directory if it is empty"}
    description = "Initialize pocok project, pocok.yml and docker-compose.yml will be created if they don't exist."

    def prepare_states(self):
        StateHolder.name = FileUtils.get_parameter_or_directory_name('<name>')
        StateHolder.work_dir = StateHolder.base_work_dir
        StateUtils.prepare(["config", "catalog", "project_repo"])

    def resolve_dependencies(self):
        pass

    def execute(self):
        if StateHolder.repository is not None:
            target_file = os.path.join(ProjectUtils.get_target_dir(StateHolder.catalog_element),
                                       StateHolder.catalog_element.get('file', 'pocok.yml'))
            if not os.path.exists(target_file):
                ProjectInit.fix_file(target_file)
        else:
            file = FileUtils.get_backward_compatible_pocok_file(directory=os.getcwd())
            if file is None:
                ProjectInit.fix_file(os.path.join(os.getcwd(), 'pocok.yml'))
        ColorPrint.print_info("Project init completed")

    @staticmethod
    def fix_file(target_file):
        if not os.path.exists(target_file):
            src_file = os.path.join(os.path.dirname(__file__), '../services/resources/pocok.yml')
            shutil.copyfile(src=src_file, dst=target_file)
            default_compose = os.path.join(os.path.dirname(target_file), 'docker-compose.yml')
            if not os.path.exists(default_compose):
                src_file = os.path.join(os.path.dirname(__file__), '../services/resources/docker-compose.yml')
                shutil.copyfile(src=src_file, dst=default_compose)

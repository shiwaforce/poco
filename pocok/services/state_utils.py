import os
import yaml
from .catalog_handler import CatalogHandler
from .config_handler import ConfigHandler
from .console_logger import ColorPrint
from .file_utils import FileUtils
from .project_utils import ProjectUtils
from .state import StateHolder


class StateUtils:

    @staticmethod
    def prepare(preparable=None):
        if preparable is None or len(preparable) == 0:
            ColorPrint.print_info(message="Empty prepare object", lvl=1)
            return
        for elem in preparable:
            if elem is "config":
                StateUtils.prepare_config()
            elif elem in ["catalog_read", "catalog"]:
                StateUtils.prepare_catalog(elem)
            elif elem is "project_repo":
                StateUtils.prepare_project_repo()
            else:
                ColorPrint.print_info(message="Unknown prepare command : " + str(elem))

        if StateHolder.args.get("--offline"):
            StateHolder.offline = StateHolder.args.get("--offline")

        if StateHolder.args.get("--always-update"):
            StateHolder.always_update = StateHolder.args.get("--always-update")

    @staticmethod
    def prepare_config():
        if StateHolder.global_config_file is None:
            StateHolder.global_config_file = os.path.join(StateHolder.home_dir, '.pocok')
        StateUtils.prepare_config_handler()
        StateHolder.config_handler.read_configs(StateHolder.global_config_file, True)

    @staticmethod
    def prepare_catalog(elem):
        if StateHolder.catalog_config_file is None:
            StateHolder.catalog_config_file = os.path.join(StateHolder.home_dir, 'config')
        StateUtils.prepare_config_handler()
        if os.path.exists(StateHolder.catalog_config_file):
            StateHolder.config_handler.read_catalogs()
            if elem is "catalog":
                CatalogHandler.load()

    @staticmethod
    def prepare_project_repo():
        """Get project parameters form catalog, if it is exists"""

        if StateHolder.name is None:
            return
        for catalog in StateHolder.catalogs:
            if StateHolder.name in StateHolder.catalogs[catalog]:
                StateHolder.catalog_element = StateHolder.catalogs[catalog].get(StateHolder.name)

        if StateHolder.catalog_element is None:
            return
        StateHolder.repository = ProjectUtils.get_project_repository(StateHolder.catalog_element, ssh=None)
        # TODO handle ssh parameter

    @staticmethod
    def prepare_config_handler():
        if StateHolder.config_handler is None:
            ConfigHandler()







    @staticmethod
    def fill_states():
        if '<project/plan>' in StateHolder.args:
            StateUtils.calculate_name_and_work_dir()

        if StateHolder.config is not None:
            StateUtils.read_project_config_and_catalog()

    @staticmethod
    def calculate_name_and_work_dir():
        arg = StateHolder.args.get('<project/plan>')
        if arg is None:  # if empty
            StateHolder.work_dir = os.getcwd()
            StateHolder.name = FileUtils.get_directory_name()
        elif '/' in arg:  # if have '/'
            project_and_plan = arg.split("/", maxsplit=2)
            StateHolder.name = project_and_plan[0]
            StateHolder.plan = project_and_plan[1]
        else:  # if need some another checks
            local_project_file = FileUtils.get_file_with_extension('pocok')
            if local_project_file is None:
                StateHolder.name = arg
            else:
                if StateUtils.check_file(local_project_file, arg):
                    StateHolder.work_dir = os.getcwd()
                    StateHolder.name = FileUtils.get_directory_name()
                    StateHolder.plan = arg
                else:
                    StateHolder.name = arg

    @staticmethod
    def check_file(file, plan):  # TODO move to another utils!
        with open(file) as stream:
            try:
                project_config = yaml.load(stream=stream)

                if 'plan' not in project_config:
                    return False
                if not isinstance(project_config['plan'], dict):
                    return False
                return plan in project_config['plan']
            except yaml.YAMLError as exc:
                return False

    @staticmethod
    def read_project_config_and_catalog():
        CatalogHandler.load()
        if StateHolder.name is not None:
            catalog = CatalogHandler.get()
            if catalog is not None:
                StateHolder.config_handler.read_configs(
                    os.path.join(StateHolder.work_dir, catalog.get('repository_dir', StateHolder.name), '.pocok'))
        else:
            """ Read local config """
            StateHolder.config_handler.read_configs(os.path.join(os.getcwd(), '.pocok'))



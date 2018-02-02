import os
import yaml
from .catalog_handler import CatalogHandler
from .config_handler import ConfigHandler
from .file_utils import FileUtils
from .state import StateHolder


class StateUtils(object):

    @staticmethod
    def fill_pre_states():
        StateHolder.catalog_config_file = os.path.join(StateHolder.home_dir, 'config')
        StateHolder.global_config_file = os.path.join(StateHolder.home_dir, '.pocok')

    @staticmethod
    def fill_states():
        config_handler = ConfigHandler()
        config_handler.read_configs(StateHolder.global_config_file, True)

        if '<project/plan>' in StateHolder.args:
            StateUtils.calculate_name_and_work_dir()
        elif '<project>' in StateHolder.args:
            StateHolder.name = FileUtils.get_parameter_or_directory_name('<project>')
            StateHolder.work_dir = StateHolder.base_work_dir
        else:
            StateHolder.work_dir = StateHolder.base_work_dir

        """ Always parse catalog """
        if ConfigHandler.exists():
            config_handler.read_catalogs()

        if StateHolder.args.get("--offline"):
            StateHolder.offline = StateHolder.args.get("--offline")

        if StateHolder.args.get("--always-update"):
            StateHolder.always_update = StateHolder.args.get("--always-update")

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
            local_project_file = FileUtils.get_exists_file_full_name(os.getcwd(), 'pocok', ['yml', 'yaml'])
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
            StateHolder.config_handler.read_configs(
                os.path.join(StateHolder.work_dir, catalog.get('repository_dir', StateHolder.name), '.pocok'))
        else:
            """ Read local config """
            StateHolder.config_handler.read_configs(os.path.join(os.getcwd(), '.pocok'))



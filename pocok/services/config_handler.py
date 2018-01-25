import os
import shutil
import yaml
from .console_logger import Doc, ColorPrint
from .file_utils import FileUtils
from .state import StateHolder
from .yaml_handler import YamlHandler


class ConfigHandler(object):

    MODES = {
        'developer': {
            'offline': False,
            'always_update': False
        },
        'demo': {
            'offline': False,
            'always_update': True
        },
        'server': {
            'offline': True,
            'always_update': False
        }

    }

    def __init__(self):
        StateHolder.config_parsed = False
        StateHolder.config_handler = self

    @staticmethod
    def read_catalogs():
        """Parse local configuration file"""
        if not StateHolder.config_parsed:
            config = YamlHandler.read(file=StateHolder.catalog_config_file, doc=Doc.CATALOGS_CONFIG)

            if not type(config) is dict:
                config['default'] = {}
            StateHolder.config = dict(config)
            StateHolder.config_parsed = True

    @staticmethod
    def read_configs(config_file, check_wd=False):
        if os.path.isdir(config_file):
            os.path.join(config_file, '.poco')
        if not os.path.exists(config_file):
            ColorPrint.print_info("Config file not exists: " + config_file, 1)
            return
        config = YamlHandler.read(file=config_file, doc=Doc.CONFIG)

        if check_wd:
            workspace = config.get('workspace')
            if workspace is not None:
                StateHolder.base_work_dir = workspace
            if not (os.path.exists(path=StateHolder.base_work_dir)):
                os.makedirs(StateHolder.work_dir)

        ''' mode and specific parameters '''
        if 'mode' in config and str(config['mode']).lower() in ConfigHandler.MODES.keys():
            StateHolder.mode = str(config['mode']).lower()
            for key, value in ConfigHandler.MODES[StateHolder.mode].items():
                setattr(StateHolder, key, value)

    def set_branch(self, branch, config=None):
        """Set catalog actual branch"""
        self.read_catalogs()
        if config is None:
            if 'default' in StateHolder.config:
                config = 'default'
            else:
                config = StateHolder.config[list(StateHolder.config.keys())[0]]

        if config not in list(StateHolder.config.keys()):
            ColorPrint.exit_after_print_messages(message="Catalog not exists with name: " + config)
            StateHolder.config[config]['branch'] = branch
        YamlHandler.write(file=StateHolder.catalog_config_file, data=StateHolder.config)

    def init(self):
        """Check home directory"""
        if not ConfigHandler.exists():
            ColorPrint.print_info(message="Default catalog configuration initialized: "
                                          + str(StateHolder.catalog_config_file))
            if not os.path.exists(StateHolder.home_dir):
                os.mkdir(StateHolder.home_dir)
            if not os.path.exists(StateHolder.catalog_config_file):
                src_file = os.path.join(os.path.dirname(__file__), 'resources/config')
                shutil.copyfile(src=src_file, dst=StateHolder.catalog_config_file)
                StateHolder.config_parsed = False
        self.read_catalogs()
        '''Check file type catalog'''
        for config in StateHolder.config:
            conf = StateHolder.config[config]
            if type(conf) is not dict:
                continue
            if conf.get("repositoryType", "file") is "file":
                # TODO
                FileUtils.make_empty_file_with_empty_dict(directory=StateHolder.home_dir,
                                                          file=conf.get('file', 'pocok-catalog.yml'))

    def handle_command(self):

        if StateHolder.has_args('init'):
            self.init()
            return

        # TODO
        if StateHolder.has_args('config'):
            if StateHolder.config is None:
                ColorPrint.exit_after_print_messages('catalog config commands works only with config file.\n '
                                                     'Run "catalog init" command to create one.')
            if StateHolder.has_args('remove'):
                self.remove(StateHolder.args.get('<catalog>'))
            if StateHolder.has_args('add'):
                self.add()
            ColorPrint.print_info(self.print_config())
            return

    @staticmethod
    def remove(catalog):
        if catalog not in list(StateHolder.config.keys()):
            ColorPrint.exit_after_print_messages(message="Catalog not exists with name: " + catalog)
        del StateHolder.config[catalog]
        YamlHandler.write(file=StateHolder.catalog_config_file, data=StateHolder.config)

    @staticmethod
    def add():
        catalog = StateHolder.args.get('<catalog>')
        if catalog in list(StateHolder.config.keys()):
            StateHolder.config.remove(catalog)
        config = dict()
        config['repositoryType'] = 'git'
        config['server'] = StateHolder.args.get('<git-url>')
        if StateHolder.args.get('<branch>') is not None:
            config['branch'] = StateHolder.args.get('<branch>')
        if StateHolder.args.get('<file>') is not None:
            config['file'] = StateHolder.args.get('<file>')
        StateHolder.config[catalog] = config
        YamlHandler.write(file=StateHolder.catalog_config_file, data=StateHolder.config)

    @staticmethod
    def print_config():
        config = "Actual config\n"
        config += "-------------\n\n"
        config += "Project name: " + str(StateHolder.name) + "\n"
        config += "Working directory: " \
                  + str(StateHolder.work_dir if StateHolder.work_dir is not None else StateHolder.base_work_dir) + "\n"
        config += "Mode: " + str(StateHolder.mode) + "\n"
        config += "Offline: " + str(StateHolder.offline) + "\n"
        config += "Always update: " + str(StateHolder.always_update) + "\n"
        if StateHolder.config is not None:
            config += "Config location: " + str(StateHolder.catalog_config_file) + "\n"
            config += "Config:\n"
            config += "-------\n"
            config += yaml.dump(StateHolder.config, default_flow_style=False, default_style='', indent=4)
        return config

    @staticmethod
    def exists():
        return os.path.exists(path=StateHolder.home_dir) and os.path.exists(path=StateHolder.catalog_config_file)

    @staticmethod
    def str2bool(val):
        return str(val).lower() in ("yes", "true", "t", "1")

import os
import yaml
from .console_logger import Doc, ColorPrint
from .file_utils import FileUtils
from .state import StateHolder
from .yaml_utils import YamlUtils


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

    @staticmethod
    def read_catalogs():
        """Parse local configuration file"""
        if not StateHolder.config_parsed:
            config = YamlUtils.read(file=StateHolder.catalog_config_file, doc=Doc.CATALOGS_CONFIG)

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
        config = YamlUtils.read(file=config_file, doc=Doc.CONFIG)
        if check_wd:
            ConfigHandler.check_wd(config=config)

        ''' mode and specific parameters '''
        if 'mode' in config and str(config['mode']).lower() in ConfigHandler.MODES.keys():
            StateHolder.mode = str(config['mode']).lower()
            for key, value in ConfigHandler.MODES[StateHolder.mode].items():
                setattr(StateHolder, key, value)

    @staticmethod
    def check_wd(config):
        workspace = config.get('workspace')
        if workspace is not None:
            if StateHolder.base_work_dir == StateHolder.work_dir:
                StateHolder.work_dir = workspace
            StateHolder.base_work_dir = workspace
        if not (os.path.exists(path=StateHolder.base_work_dir)):
            os.makedirs(StateHolder.base_work_dir)

    @staticmethod
    def set_branch(branch, config=None):
        """Set catalog actual branch"""
        ConfigHandler.read_catalogs()
        if config is None:
            if 'default' in StateHolder.config:
                config = 'default'
            else:
                config = StateHolder.config[list(StateHolder.config.keys())[0]]

        ConfigHandler.check_name(config)
        if StateHolder.config[config]['repositoryType'] == 'file':
            ColorPrint.exit_after_print_messages(message="Branch is not supported in this repository.")
        StateHolder.config[config]['branch'] = branch
        YamlUtils.write(file=StateHolder.catalog_config_file, data=StateHolder.config)

    @staticmethod
    def check_name(name):
        if name not in list(StateHolder.config.keys()):
            ColorPrint.exit_after_print_messages(message="Catalog not exists with name: " + name)

    @staticmethod
    def init():
        """Check home directory"""
        if not ConfigHandler.exists():
            ColorPrint.print_info(message="Catalog configuration initialized: " + str(StateHolder.catalog_config_file))
            if not os.path.exists(StateHolder.home_dir):
                os.mkdir(StateHolder.home_dir)
            if not os.path.exists(StateHolder.catalog_config_file):
                FileUtils.make_empty_file_with_empty_dict(StateHolder.home_dir, 'config')
                StateHolder.config_parsed = False
        ConfigHandler.read_catalogs()
        ConfigHandler.check_catalogs()

    @staticmethod
    def check_catalogs():
        """Check file type catalog"""
        for config in StateHolder.config:
            conf = StateHolder.config[config]
            if type(conf) is not dict:
                continue
            if conf.get("repositoryType", "file") is "file":
                FileUtils.make_empty_file_with_empty_dict(directory=StateHolder.home_dir,
                                                          file=conf.get('file', 'poco-catalog.yml'))

    @staticmethod
    def add(new_config):
        catalog = StateHolder.args.get('<name>')
        modify = StateHolder.has_args('modify')

        if StateHolder.config is None:  # init if not exists
            ConfigHandler.init()

        if catalog not in list(StateHolder.config.keys()) and modify:
            ColorPrint.exit_after_print_messages('Catalog with name: "' + str(catalog) + '" not exists in config')
        if catalog in list(StateHolder.config.keys()) and not modify:
            ColorPrint.exit_after_print_messages('Catalog with name: "' + str(catalog) + '" is exists')
        StateHolder.config[catalog] = new_config
        YamlUtils.write(file=StateHolder.catalog_config_file, data=StateHolder.config)
        ColorPrint.print_info(ConfigHandler.print_config())

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

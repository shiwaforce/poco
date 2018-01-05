import os
import shutil
import yaml
from .console_logger import Doc, ColorPrint
from .file_utils import FileUtils
from .state import StateHolder
from .yaml_handler import YamlHandler


class ConfigHandler(object):

    config = None

    def __init__(self):
        StateHolder.config_parsed = False
        StateHolder.config_handler = self

    def read_catalogs(self):
        """Parse local configuration file"""
        if not StateHolder.config_parsed:
            self.config = YamlHandler.read(file=StateHolder.catalog_config_file, doc=Doc.CATALOGS_CONFIG)

            if not type(self.config) is dict:
                self.config['default'] = {}
            StateHolder.config = dict(self.config)
            StateHolder.config_parsed = True

    @staticmethod
    def read_configs(config_file):
        if not os.path.exists(config_file):
            return
        config = YamlHandler.read(file=config_file, doc=Doc.CONFIG)

        if 'workspace' in config:
            StateHolder.work_dir = config.get('workspace')

        if not (os.path.exists(path=StateHolder.work_dir)):
            os.makedirs(StateHolder.work_dir)

        if 'developer-mode' in config:
            StateHolder.developer_mode = ConfigHandler.str2bool(config['developer-mode'])

    def set_branch(self, branch, config=None):
        """Set catalog actual branch"""
        self.read_catalogs()
        if config is None:
            if 'default' in self.config:
                config = 'default'
            else:
                config = self.config[list(self.config.keys())[0]]

        if config not in list(self.config.keys()):
            ColorPrint.exit_after_print_messages(message="Catalog not exists with name: " + config)
        self.config[config]['branch'] = branch
        YamlHandler.write(file=StateHolder.catalog_config_file, data=self.config)

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
        for config in self.config:
            conf = self.config[config]
            if type(conf) is not dict:
                continue
            if conf.get("repositoryType", "file") is "file":
                FileUtils.make_empty_file_with_empty_dict(directory=StateHolder.home_dir,
                                                          file=conf.get('file', 'poco-catalog.yml'))

    def handle_command(self):

        if StateHolder.has_args('init'):
            self.init()
            return

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

    def remove(self, catalog):
        if catalog not in list(self.config.keys()):
            ColorPrint.exit_after_print_messages(message="Catalog not exists with name: " + catalog)
        del self.config[catalog]
        YamlHandler.write(file=StateHolder.catalog_config_file, data=self.config)

    def add(self):
        catalog = StateHolder.args.get('<catalog>')
        if catalog in list(self.config.keys()):
            self.config.remove(catalog)
        config = dict()
        config['repositoryType'] = 'git'
        config['server'] = StateHolder.args.get('<git-url>')
        if StateHolder.args.get('<branch>') is not None:
            config['branch'] = StateHolder.args.get('<branch>')
        if StateHolder.args.get('<file>') is not None:
            config['file'] = StateHolder.args.get('<file>')
        self.config[catalog] = config
        YamlHandler.write(file=StateHolder.catalog_config_file, data=self.config)

    def print_config(self):
        config = "Actual config\n"
        config += "-------------\n\n"
        config += "Working directory " + str(StateHolder.work_dir) + "\n"
        config += "Offline: " + str(StateHolder.offline) + "\n"
        config += "Developer mode: " + str(StateHolder.developer_mode) + "\n"
        config += "Project name: " + str(StateHolder.name) + "\n"
        if StateHolder.config is not None:
            config += "Config location: " + str(StateHolder.catalog_config_file) + "\n"
            config += "Config:\n"
            config += "-------\n"
            config += yaml.dump(self.config, default_flow_style=False, default_style='', indent=4)
        return config

    @staticmethod
    def exists():
        return os.path.exists(path=StateHolder.home_dir) and os.path.exists(path=StateHolder.catalog_config_file)

    @staticmethod
    def str2bool(val):
        return str(val).lower() in ("yes", "true", "t", "1")

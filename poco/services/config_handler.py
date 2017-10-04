import os
import shutil
from .console_logger import Doc, ColorPrint
from .file_utils import FileUtils
from .state import StateHolder
from .yaml_handler import YamlHandler


class ConfigHandler(object):

    config = None

    def __init__(self):
        StateHolder.config_parsed = False

        if not ConfigHandler.exists():
            self.init()
        if not os.path.exists(StateHolder.log_dir):
            os.mkdir(StateHolder.log_dir)

    def read(self):
        """Parse local configuration file"""
        if not StateHolder.config_parsed:
            self.config = YamlHandler.read(file=StateHolder.config_file, doc=Doc.CONFIG)

            if not type(self.config) is dict:
                self.config['default'] = {}

            if 'workspace' not in self.config:
                StateHolder.work_dir = os.path.join(os.path.expanduser(path='~'), 'workspace')
                self.config['workspace'] = StateHolder.work_dir
                YamlHandler.write(file=StateHolder.config_file, data=self.config)
            else:
                StateHolder.work_dir = self.config.get('workspace')
            if not (os.path.exists(path=StateHolder.work_dir)):
                os.makedirs(StateHolder.work_dir)

            StateHolder.config = dict(self.config)
            del StateHolder.config['workspace']

            if 'developer-mode' in self.config:
                StateHolder.developer_mode = ConfigHandler.str2bool(self.config['developer-mode'])
                del StateHolder.config['developer-mode']

            StateHolder.config_parsed = True

    def set_branch(self, branch, config=None):
        """Set catalog actual branch"""
        self.read()
        if config is None:
            if 'default' in self.config:
                config = 'default'
            else:
                config = self.config[list(self.config.keys())[0]]

        if config not in self.config.keys():
            ColorPrint.exit_after_print_messages(message="Config section not exists with name: " + config)
        self.config[config]['branch'] = branch
        YamlHandler.write(file=StateHolder.config_file, data=self.config)

    def init(self):
        """Check home directory"""
        if not ConfigHandler.exists():
            ColorPrint.print_info(message="Default configuration initialized: " + str(StateHolder.config_file))
            if not os.path.exists(StateHolder.home_dir):
                os.mkdir(StateHolder.home_dir)
            if not os.path.exists(StateHolder.config_file):
                src_file = os.path.join(os.path.dirname(__file__), 'resources/config')
                shutil.copyfile(src=src_file, dst=StateHolder.config_file)
                StateHolder.config_parsed = False
        self.read()
        '''Check file type catalog'''
        for config in self.config:
            conf = self.config[config]
            if type(conf) is not dict:
                continue
            if conf.get("repositoryType", "file") is "file":
                FileUtils.make_empty_file_with_empty_dict(directory=StateHolder.home_dir,
                                                          file=conf.get('file', 'poco-catalog.yml'))

    def dump(self):
        YamlHandler.dump(data=self.config)

    @staticmethod
    def exists():
        return os.path.exists(path=StateHolder.home_dir) and os.path.exists(path=StateHolder.config_file)

    @staticmethod
    def str2bool(val):
        return str(val).lower() in ("yes", "true", "t", "1")

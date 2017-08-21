import os
import shutil
from .abstract_yaml import AbstractYamlHandler
from .console_logger import Doc, ColorPrint
from .file_utils import FileUtils


class ConfigHandler(AbstractYamlHandler):

    config = None
    default_config = None
    work_dir = None

    def __init__(self, home_dir):
        self.parsed = False
        self.home_dir = home_dir
        self.log_dir = os.path.join(self.home_dir, 'logs')
        super(ConfigHandler, self).__init__(os.path.join(self.home_dir, 'config'))

        if not self.exists():
            self.init()
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

    def read(self):
        """Parse local configuration file"""
        if not self.parsed:
            self.config = super(ConfigHandler, self).read(doc=Doc.CONFIG)

            if type(self.config) is dict:
                if 'default' in self.config:
                    self.default_config = self.config['default']
                self.default_config = self.config[list(self.config.keys())[0]]
            else:
                self.config['default'] = {}
                self.default_config = {}

            if 'workspace' not in self.config:
                self.work_dir = os.path.join(os.path.expanduser(path='~'), 'workspace')
                self.config['workspace'] = self.work_dir
                super(ConfigHandler, self).write(self.config)
            else:
                self.work_dir = self.config.get('workspace')
            if not (os.path.exists(path=self.work_dir)):
                os.makedirs(self.work_dir)
            self.parsed = True

    def set_branch(self, branch, config=None):
        """Set catalog actual branch"""
        self.read()
        if config is None:
            self.default_config['branch'] = branch
        else:
            if config not in self.config.keys():
                ColorPrint.exit_after_print_messages(message="Config section not exists with name: " + config)
            self.config[config]['branch'] = branch
            self.write(self.config)

    def get_config(self):
        """Get the full content of config file"""
        self.read()
        return self.config

    def get_work_dir(self):
        self.read()
        return self.work_dir

    def exists(self):
        return os.path.exists(path=self.home_dir) and os.path.exists(path=self.file)

    def init(self):
        """Check home directory"""
        if not self.exists():
            ColorPrint.print_info(message="Default configuration initialized: " + str(self.file))
            if not os.path.exists(self.home_dir):
                os.mkdir(self.home_dir)
            if not os.path.exists(self.file):
                src_file = os.path.join(os.path.dirname(__file__), 'resources/config')
                shutil.copyfile(src=src_file, dst=self.file)
                self.parsed = False
        self.read()
        '''Check file type catalog'''
        for config in self.config:
            conf = self.config[config]
            if type(conf) is not dict:
                continue
            if conf.get("repositoryType", "file") is "file":
                FileUtils.make_empty_file_with_empty_dict(directory=self.home_dir,
                                                          file=conf.get('file', 'project-catalog.yml'))


import os
import shutil
from .abstract_yaml import AbstractYamlHandler
from .console_logger import Doc, ColorPrint
from .environment_utils import EnvironmentUtils
from .file_utils import FileUtils


class ConfigHandler(AbstractYamlHandler):

    config = None
    actual_config = None
    work_dir = None

    def __init__(self, home_dir):
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
            '''TODO if we want handle multiple config, need refactor here'''
            if 'default' in self.config:
                self.actual_config = self.config['default']

                if self.actual_config is None:
                    self.config['default'] = {}
                    self.actual_config = {}

                if 'workspace' not in self.actual_config:
                    self.work_dir = os.path.join(os.path.expanduser(path='~'), 'workspace')
                    self.config['default']['workspace'] = self.work_dir
                    super(ConfigHandler, self).write(self.config)
                else:
                    self.work_dir = self.actual_config.get('workspace')
                if not (os.path.exists(path=self.work_dir)):
                    os.makedirs(self.work_dir)

    def get_repository_type(self):
        """Get catalog repository type (or file)"""
        self.read()
        if self.actual_config is not None and "repositoryType" in self.actual_config:
            if 'git' == self.actual_config["repositoryType"]:
                return 'git'
            elif 'svn' == self.actual_config["repositoryType"]:
                return 'svn'
        return 'file'

    def get_url(self):
        """Get catalog URL if its an remote repository"""
        self.read()
        if self.actual_config is not None and "server" in self.actual_config:
            return self.actual_config['server']
        return EnvironmentUtils.get_variable('PROJECT_CATALOG')

    def get_branch(self):
        """Get catalog branch if its an remote repository"""
        self.read()
        if self.actual_config is not None:
            return self.actual_config.get('branch', 'master')
        return 'master'

    def set_branch(self, branch):
        """Set catalog actual branch"""
        self.read()
        if self.actual_config is not None:
            self.actual_config['branch'] = branch
        self.write(self.config)

    def get_catalog_file(self):
        """Get catalog file"""
        self.read()
        if self.actual_config is not None and self.get_repository_type() == 'file':
            return self.actual_config.get('file', 'project-catalog.yml')
        return None

    def get_config(self):
        """Get the full content of config file"""
        self.read()
        return self.config

    def get_actual_config(self):
        """Get actual config (default now)"""
        self.read()
        return self.actual_config

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
            self.read()

        '''Check file type catalog'''
        if self.get_repository_type() == "file":
            FileUtils.make_empty_file_with_empty_dict(directory=self.home_dir, file=self.get_catalog_file())


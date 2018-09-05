import unittest
import copy
import os
import sys
import shutil
import tempfile
import yaml
from contextlib import contextmanager
import poco.poco as poco
from ..services.file_utils import FileUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class AbstractTestSuite(unittest.TestCase):

    LOCAL_CONFIG = {
        'default': {
            'repositoryType': 'file',
            'file': 'poco-catalog.yml',
        }
    }

    REMOTE_CONFIG = {
      'default': {
        'repositoryType': 'git',
        'file': 'poco-catalog.yml',
        'server': 'https://github.com/shiwaforce/poco-example.git',
        'branch': 'master'
        }
    }

    POCO_CONFIG = {
        'mode': 'developer'
    }

    STACK_LIST_SAMPLE = {
        'nginx': {
            'file': 'nginx/poco.yml',
            'git': 'https://github.com/shiwaforce/poco-example.git',
            'repository_dir': 'poco-example'
        },
        'mysql': {
            'file': 'mysql/poco.yml',
            'git': 'https://github.com/shiwaforce/poco-example.git',
            'repository_dir': 'poco-example'
        }
    }

    @contextmanager
    def captured_output(self):
        new_out, new_err = StringIO(), StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='poco-home')
        self.config_file = os.path.join(self.tmpdir, 'config')
        self.poco_file = os.path.join(self.tmpdir, '.poco')
        self.local_stack_list = os.path.join(self.tmpdir, 'poco-catalog.yml')
        self.ws_dir = os.path.join(self.tmpdir, 'ws')
        os.makedirs(self.ws_dir)
        self.orig_dir = os.getcwd()
        os.chdir(self.ws_dir)

        self.clean_states()
        StateHolder.base_work_dir = self.ws_dir

    def tearDown(self):
        os.chdir(self.orig_dir)
        try:
            shutil.rmtree(self.tmpdir, onerror=FileUtils.remove_readonly)
        except Exception:
            ColorPrint.print_warning("Failed to delete test directory: " + self.tmpdir)

    @staticmethod
    def clean_states():

        StateHolder.home_dir = None
        StateHolder.catalog_config_file = None
        StateHolder.global_config_file = None
        StateHolder.repositories = dict()
        StateHolder.args = dict()
        StateHolder.base_work_dir = os.path.join(os.path.expanduser(path='~'), 'workspace')
        StateHolder.work_dir = None
        StateHolder.config_parsed = False
        StateHolder.config = None
        StateHolder.catalogs = None
        StateHolder.catalog_element = None
        StateHolder.mode = None
        StateHolder.offline = False
        StateHolder.always_update = True
        StateHolder.name = None
        StateHolder.plan = None
        StateHolder.repository = None
        StateHolder.container_mode = "Docker"
        StateHolder.test_mode = False
        StateHolder.compose_handler = None

        StateHolder.catalog_repositories = dict()
        StateHolder.default_catalog_repository = None

    def init_with_local_catalog(self, params=None):
        with open(self.config_file, 'w+') as stream:
            yaml.dump(data=AbstractTestSuite.LOCAL_CONFIG, stream=stream, default_flow_style=False, default_style='',
                      indent=4)
        with open(self.local_stack_list, 'w+') as stream:
            yaml.dump(data=AbstractTestSuite.STACK_LIST_SAMPLE, stream=stream, default_flow_style=False,
                      default_style='', indent=4)
        self.init_poco_config(params)

    def init_with_remote_catalog(self, params=None):
        with open(self.config_file, 'w+') as stream:
            yaml.dump(data=AbstractTestSuite.REMOTE_CONFIG, stream=stream, default_flow_style=False, default_style='',
                      indent=4)
        self.init_poco_config(params)

    def init_poco_config(self, params):
        with open(self.poco_file, 'w+') as stream:
            config = copy.deepcopy(self.POCO_CONFIG)
            config["workspace"] = self.ws_dir
            if params is not None:
                if isinstance(params, dict):
                    config.update(params)
            yaml.dump(data=config, stream=stream, default_flow_style=False, default_style='',
                      indent=4)

    def run_poco_command(self, *args):
        runnable = poco.Poco(home_dir=self.tmpdir, argv=list(args))
        runnable.start_flow()

    def init_empty_compose_file(self):
        compose_file = dict()
        compose_file['services'] = dict()
        with open(os.path.join(self.ws_dir, 'docker-compose.yaml'), 'w+') as stream:
            yaml.dump(data=compose_file, stream=stream, default_flow_style=False,
                      default_style='', indent=4)

    def init_poco_file(self):
        poco_file = dict()
        poco_file['plan'] = dict()
        poco_file['plan']['default'] = 'docker-compose.yaml'
        with open(os.path.join(self.ws_dir, 'poco.yaml'), 'w+') as stream:
            yaml.dump(data=poco_file, stream=stream, default_flow_style=False,
                      default_style='', indent=4)

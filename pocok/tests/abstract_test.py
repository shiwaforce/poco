import unittest
import os
import sys
import shutil
import tempfile
import yaml
from contextlib import contextmanager
import pocok.pocok as pocok;
from ..services.file_utils import FileUtils
from ..services.state import StateHolder
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class AbstractTestSuite(unittest.TestCase):
    LOCAL_CONFIG = {
        'default': {
            'repositoryType': 'file',
            'file': 'pocok-catalog.yml',
        }
    }

    REMOTE_CONFIG = {  # TODO rename to pocok
      'default': {
        'repositoryType': 'git',
        'file': 'poco-catalog.yml',
        'server': 'https://github.com/shiwaforce/poco-example.git',
        'branch': 'master'
        }
    }

    POCOK_CONFIG = {
        'mode': 'developer'
    }

    STACK_LIST_SAMPLE = {
        'nginx': {
            'file': 'nginx/pocok-compose.yml',
            'git': 'https://github.com/shiwaforce/pocok-example.git',
            'repository_dir': 'pocok-example'
        },
        'mysql': {
            'file': 'mysql/pocok-compose.yml',
            'git': 'https://github.com/shiwaforce/pocok-example.git',
            'repository_dir': 'pocok-example'
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
        self.tmpdir = tempfile.mkdtemp(prefix='pocok-home')
        self.config_file = os.path.join(self.tmpdir, 'config')
        self.pocok_file = os.path.join(self.tmpdir, '.pocok')
        self.local_stack_list = os.path.join(self.tmpdir, 'pocok-catalog.yml')
        self.ws_dir = os.path.join(self.tmpdir, 'ws')
        os.makedirs(self.ws_dir)
        os.chdir(self.ws_dir)

        self.clean_states()
        StateHolder.base_work_dir = self.ws_dir

    def tearDown(self):
        shutil.rmtree(self.tmpdir, onerror=FileUtils.remove_readonly)

    @staticmethod
    def clean_states():
        StateHolder.home_dir = None
        StateHolder.container_mode = "Docker"
        StateHolder.config_file = None
        StateHolder.work_dir = None
        StateHolder.config_parsed = False
        StateHolder.args = dict()
        StateHolder.config = None
        StateHolder.catalogs = None
        StateHolder.catalog_element = None
        StateHolder.name = None
        StateHolder.offline = False
        StateHolder.always_update = True
        StateHolder.skip_docker = False
        StateHolder.config_handler = None
        StateHolder.compose_handler = None

    def init_with_local_catalog(self):
        with open(self.config_file, 'w+') as stream:
            yaml.dump(data=AbstractTestSuite.REMOTE_CONFIG, stream=stream, default_flow_style=False, default_style='',
                      indent=4)
        with open(self.local_stack_list, 'w+') as stream:
            yaml.dump(data=AbstractTestSuite.STACK_LIST_SAMPLE, stream=stream, default_flow_style=False,
                      default_style='', indent=4)
        self.init_pocok_config()

    def init_with_remote_catalog(self):
        with open(self.config_file, 'w+') as stream:
            yaml.dump(data=AbstractTestSuite.REMOTE_CONFIG, stream=stream, default_flow_style=False, default_style='',
                      indent=4)
        self.init_pocok_config()

    def init_pocok_config(self):
        with open(self.pocok_file, 'w+') as stream:
            config = self.POCOK_CONFIG
            config["workspace"] = self.ws_dir
            yaml.dump(data=AbstractTestSuite.POCOK_CONFIG, stream=stream, default_flow_style=False, default_style='',
                      indent=4)

    def run_pocok_command(self, *args):
        runnable = pocok.Pocok(home_dir=self.tmpdir, argv=list(args))
        runnable.run()
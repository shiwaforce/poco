import unittest
import os
import sys
import shutil
import tempfile
import yaml
from contextlib import contextmanager
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
        'server': 'https://github.com/shiwaforce/project-compose-example.git',
        'branch': 'master'
        }
    }

    STACK_LIST_SAMPLE = {
        'nginx': {
            'file': 'nginx/project-compose.yml',
            'git': 'https://github.com/shiwaforce/project-compose-example.git',
            'repository_dir': 'project-compose-example'
        },
        'mysql': {
            'file': 'mysql/project-compose.yml',
            'git': 'https://github.com/shiwaforce/project-compose-example.git',
            'repository_dir': 'project-compose-example'
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
        self.local_stack_list = os.path.join(self.tmpdir, 'poco-catalog.yml')
        self.ws_dir = os.path.join(self.tmpdir, 'ws')
        os.makedirs(self.ws_dir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def init_with_local_catalog(self):
        data = self.add_workspace_dir(AbstractTestSuite.LOCAL_CONFIG)
        with open(self.config_file, 'w+') as stream:
            yaml.dump(data=data, stream=stream, default_flow_style=False, default_style='',
                      indent=4)
        with open(self.local_stack_list, 'w+') as stream:
            yaml.dump(data=AbstractTestSuite.STACK_LIST_SAMPLE, stream=stream, default_flow_style=False,
                      default_style='', indent=4)

    def init_with_remote_catalog(self):
        data = self.add_workspace_dir(AbstractTestSuite.REMOTE_CONFIG)
        with open(self.config_file, 'w+') as stream:
            yaml.dump(data=data, stream=stream, default_flow_style=False, default_style='',
                      indent=4)

    def add_workspace_dir(self, config):
        config["workspace"] = self.ws_dir
        return config

import os.path as path
import yaml
from .console_logger import *
from .file_repository import FileRepository
from .git_repository import GitRepository
from .svn_repository import SvnRepository
from .environment_utils import EnvironmentUtils


class CatalogHandler:

    def __init__(self, home_dir, config, offline):

        self.config = config
        self.catalog_repositories = dict()
        self.default_repository = None

        self.catalogs = None
        self.offline_mode = offline
        for key in config.keys():
            # TODO refactor
            if key == 'workspace':
                continue
            conf = config[key]
            repo = self.get_repository_type(conf)

            if self.offline_mode and repo in ('git', 'svn'):
                repository = FileRepository(target_dir=path.join(home_dir, 'catalogHome', key))
            elif 'git' == repo:
                repository = GitRepository(target_dir=path.join(home_dir, 'catalogHome', key), url=self.get_url(conf),
                                           branch=self.get_branch(conf), git_ssh_identity_file=conf.get("ssh-key"))
            elif 'svn' == repo:
                repository = SvnRepository(target_dir=path.join(home_dir, 'catalogHome', key), url=self.get_url(conf))
            else:
                repository = FileRepository(target_dir=home_dir)

            if self.default_repository is None or key == 'default':
                self.default_repository = CatalogData(config=conf, repository=repository)
            self.catalog_repositories[key] = CatalogData(config=conf, repository=repository)

    def get_catalog(self):
        """Parse catalog file"""
        if self.catalogs is not None:
            return self.catalogs

        self.catalogs = dict()

        for key in self.catalog_repositories.keys():
            conf = self.catalog_repositories[key].config
            catalog_file = self.get_catalog_file(conf)
            lst = self.catalog_repositories[key].repository.get_yaml_file(file=catalog_file, create=True)
            if lst is None:
                ColorPrint.exit_after_print_messages(message="file not exists : " + str(catalog_file),
                                                     doc=Doc.CONFIG)
            if not isinstance(lst, dict):
                ColorPrint.exit_after_print_messages(message="file not valid : " + str(catalog_file),
                                                     doc=Doc.CONFIG)
            self.catalogs[key] = lst
        return self.catalogs

    def write_catalog(self, catalog):
        """Write catalog file"""
        if catalog is not None and catalog in self.get_catalog():
            string_format = yaml.dump(data=self.catalogs[catalog], default_flow_style=False)
            self.catalog_repositories[catalog].repository.write_yaml_file(self.get_catalog_file(
                self.catalog_repositories[catalog].config), string_format)

    def get(self, name):
        """Get project parameters form catalog, if it is exists"""
        for catalog in self.get_catalog():
            if name in self.catalogs[catalog]:
                return self.catalogs[catalog].get(name)
        ColorPrint.exit_after_print_messages(message="Project with name: %s not exist" % name)

    def set(self, name, modified):
        """Set project parameters and write, if it is exists"""
        for catalog in self.get_catalog():
            if name in self.catalogs[catalog]:
                self.catalogs[catalog][name] = modified
            self.write_catalog(catalog)

    def add_to_list(self, name, handler, url, catalog, file=None, repo_name=None):
        """Add project to the catalog"""
        if catalog is None:
            catalog = self.get_default_catalog()
        if catalog not in self.get_catalog():
            ColorPrint.exit_after_print_messages(message="Catalog not exists : " + str(catalog))
        lst = self.catalogs[catalog]
        lst[name] = dict()
        lst[name][handler] = str(url)
        if file is not None:
            lst[name]['file'] = file
        if repo_name is not None:
            lst[name]['repository_dir'] = repo_name
        self.write_catalog(catalog=catalog)

    def remove_from_list(self, name):
        """Remove project from catalog"""

        for catalog in self.get_catalog():
            lst = self.catalogs[catalog]
            if name in lst:
                lst.pop(name)
                self.write_catalog(catalog=catalog)
                return
        ColorPrint.exit_after_print_messages(message="Project not exists in catalog: " + name)

    def get_catalog_repository(self, catalog=None):
        if catalog is None:
            return self.default_repository.repository
        if catalog not in self.catalog_repositories:
            ColorPrint.exit_after_print_messages(message="Catalog not exists : " + str(catalog))
        else:
            return self.catalog_repositories[catalog].repository

    def push(self, catalog):
        if catalog is None:
            catalog = self.get_default_catalog()
            self.catalog_repositories[catalog].repository.push()

    def get_default_catalog(self):
        if 'default' in self.get_catalog():
            return 'default'
        return list(self.catalogs.keys())[0]

    @staticmethod
    def valid_catalog(catalog):
        if not isinstance(catalog, dict):
            return False
        for key in catalog.keys():
            if 'git' not in catalog[key]:
                return False
        return True

    @staticmethod
    def get_repository_type(config):
        """Get catalog repository type (or file)"""
        if config is not None and "repositoryType" in config:
            if 'git' == config["repositoryType"]:
                return 'git'
            elif 'svn' == config["repositoryType"]:
                return 'svn'
        return 'file'

    @staticmethod
    def get_url(config):
        """Get catalog URL if its an remote repository"""
        if config is not None and "server" in config:
            return config['server']
        return EnvironmentUtils.get_variable('POCO_CATALOG')

    @staticmethod
    def get_branch(config):
        """Get catalog branch if its an remote repository"""
        if config is not None:
            return config.get('branch', 'master')
        return 'master'

    @staticmethod
    def get_catalog_file(config):
        """Get catalog file"""
        if config is not None:
            return config.get('file', 'poco-catalog.yml')
        return None


class CatalogData:
    def __init__(self, config, repository):
        self.config = config
        self.repository = repository

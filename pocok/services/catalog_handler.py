import os
import yaml
from .console_logger import *
from .file_repository import FileRepository
from .git_repository import GitRepository
from .svn_repository import SvnRepository
from .environment_utils import EnvironmentUtils
from .file_utils import FileUtils
from .state import StateHolder


class CatalogHandler:

    def __init__(self):

        self.catalog_repositories = dict()
        self.default_repository = None

        for key in StateHolder.config.keys():
            conf = StateHolder.config[key]
            repo = self.get_repository_type(conf)

            repository = CatalogHandler.get_repository(key, repo)

            if self.default_repository is None or key == 'default':
                self.default_repository = CatalogData(config=conf, repository=repository)
            self.catalog_repositories[key] = CatalogData(config=conf, repository=repository)
        self.parse_catalog()

    def handle_command(self):

        if StateHolder.has_args('repo', 'branches'):
            self.get_catalog_repository(StateHolder.args.get('<catalog>')).print_branches()
            return
        if StateHolder.has_args('repo', 'branch'):
            branch = StateHolder.args.get('<branch>')
            catalog = StateHolder.args.get('<catalog>')
            self.get_catalog_repository(catalog=catalog).set_branch(branch=branch, force=StateHolder.args.get("-f"))
            StateHolder.config_handler.set_branch(branch=branch, config=catalog)
            ColorPrint.print_info("Branch changed")
            return

        if StateHolder.has_args('repo', 'remove'):
            self.remove_from_list()
            ColorPrint.print_info("Project removed")
            return

    def parse_catalog(self):
        """Parse catalog file"""
        StateHolder.catalogs = dict()

        for key in self.catalog_repositories.keys():
            conf = self.catalog_repositories[key].config
            if conf is None:
                continue
            catalog_file = self.get_catalog_file(conf)
            lst = self.catalog_repositories[key].repository.get_yaml_file(file=catalog_file, create=True)
            if lst is None:
                ColorPrint.exit_after_print_messages(message="file not exists : " + str(catalog_file),
                                                     doc=Doc.CONFIG)
            if not isinstance(lst, dict):
                ColorPrint.exit_after_print_messages(message="file not valid : " + str(catalog_file),
                                                     doc=Doc.CONFIG)
            StateHolder.catalogs[key] = lst

    def write_catalog(self, catalog):
        """Write catalog file"""
        if catalog is not None and catalog in StateHolder.catalogs:
            string_format = yaml.dump(data=StateHolder.catalogs[catalog], default_flow_style=False)
            self.catalog_repositories[catalog].repository.write_yaml_file(self.get_catalog_file(
                self.catalog_repositories[catalog].config), string_format)

    def set(self, modified):
        """Set project parameters and write, if it is exists"""
        for catalog in StateHolder.catalogs:
            if StateHolder.name in StateHolder.catalogs[catalog]:
                StateHolder.catalogs[catalog][StateHolder.name] = modified
            self.write_catalog(catalog)

    def add_to_list(self, name, handler, url, catalog, file=None, repo_name=None):
        """Add project to the catalog"""
        if catalog is None:
            catalog = self.get_default_catalog()
        if catalog not in StateHolder.catalogs:
            ColorPrint.exit_after_print_messages(message="Catalog not exists : " + str(catalog))
        lst = StateHolder.catalogs[catalog]
        lst[name] = dict()
        lst[name][handler] = str(url)
        if file is not None:
            lst[name]['file'] = file
        if repo_name is not None:
            lst[name]['repository_dir'] = repo_name
        self.write_catalog(catalog=catalog)

    def remove_from_list(self):
        """Remove project from catalog"""

        for catalog in StateHolder.catalogs:
            lst = StateHolder.catalogs[catalog]
            if StateHolder.name in lst:
                lst.pop(StateHolder.name)
                self.write_catalog(catalog=catalog)
                return
        ColorPrint.exit_after_print_messages(message="Project not exists in catalog: " + StateHolder.name)

    def get_catalog_repository(self, catalog=None):
        if catalog is None:
            return self.default_repository.repository
        if catalog not in self.catalog_repositories:
            ColorPrint.exit_after_print_messages(message="Catalog not exists : " + str(catalog))
        else:
            return self.catalog_repositories[catalog].repository

    @staticmethod
    def get():
        """Get project parameters form catalog, if it is exists"""
        for catalog in StateHolder.catalogs:
            if StateHolder.name in StateHolder.catalogs[catalog]:
                return StateHolder.catalogs[catalog].get(StateHolder.name)
        ColorPrint.exit_after_print_messages(message="Project with name: %s not exist" % StateHolder.name)

    @staticmethod
    def get_repository(key, repo):
        conf = StateHolder.config[key]
        if StateHolder.offline and repo in ('git', 'svn'):
            repository = FileRepository(target_dir=os.path.join(StateHolder.home_dir, 'catalogHome', key))
        elif 'git' == repo:
            repository = GitRepository(target_dir=os.path.join(StateHolder.home_dir, 'catalogHome', key),
                                       url=CatalogHandler.get_url(conf),
                                       branch=CatalogHandler.get_branch(conf),
                                       git_ssh_identity_file=conf.get("ssh-key"))
        elif 'svn' == repo:
            repository = SvnRepository(target_dir=os.path.join(StateHolder.home_dir, 'catalogHome', key),
                                       url=CatalogHandler.get_url(conf))
        else:
            repository = FileRepository(target_dir=StateHolder.home_dir)
        return repository


    @staticmethod
    def get_default_catalog():
        if 'default' in StateHolder.catalogs:
            return 'default'
        return list(StateHolder.catalogs.keys())[0]

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
        return EnvironmentUtils.get_variable('POCOK_CATALOG')

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
            #TODO
            return config.get('file', 'pocok-catalog.yml')
        return None

    @staticmethod
    def print_ls():
        """Get catalog list"""
        lst = StateHolder.catalogs
        empty = True
        for cat in lst.keys():
            if len(lst[cat].keys()) > 0:
                empty = False
                break
        if not empty:
            ColorPrint.print_with_lvl(message="-------------------", lvl=-1)
            ColorPrint.print_with_lvl(message="Available projects:", lvl=-1)
            ColorPrint.print_with_lvl(message="-------------------", lvl=-1)

            for cat in lst.keys():
                for key in lst[cat].keys():
                    msg = key
                    if os.path.exists(os.path.join(
                            StateHolder.work_dir,
                            lst[cat][key]["repository_dir"] if "repository_dir" in lst[cat][key] else key)):
                        msg += " (*)"
                    ColorPrint.print_with_lvl(message=msg, lvl=-1)
        else:
            ColorPrint.print_with_lvl(
                message="Project catalog is empty. You can add projects with 'project-catalog add' command",
                lvl=-1)


class CatalogData:
    def __init__(self, config, repository):
        self.config = config
        self.repository = repository

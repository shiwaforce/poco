import os
import yaml
from .console_logger import *
from .file_repository import FileRepository
from .git_repository import GitRepository
from .github_repository import GitHubRepository
from .gitlab_repository import GitLabRepository
from .svn_repository import SvnRepository
from .environment_utils import EnvironmentUtils
from .state import StateHolder


class CatalogHandler:

    @staticmethod
    def load():
        if StateHolder.config is None:
            return

        StateHolder.catalog_repositories = dict()
        StateHolder.default_catalog_repository = None

        for key in StateHolder.config.keys():
            conf = StateHolder.config[key]
            repo = CatalogHandler.get_repository_type(conf)

            repository = CatalogHandler.get_repository(key, repo, True)

            if StateHolder.default_catalog_repository is None or key == 'default':
                StateHolder.default_catalog_repository = CatalogData(config=conf, repository=repository)

            StateHolder.catalog_repositories[key] = CatalogData(config=conf, repository=repository)
        CatalogHandler.parse_catalog()

    @staticmethod
    def parse_catalog():
        """Parse catalog file"""
        StateHolder.catalogs = dict()

        for key in StateHolder.catalog_repositories.keys():
            conf = StateHolder.catalog_repositories[key].config
            if conf is None:
                continue
            catalog_file = CatalogHandler.get_catalog_file(conf)
            lst = StateHolder.catalog_repositories[key].repository.get_yaml_file(file=catalog_file, create=True)
            if lst is None:
                ColorPrint.exit_after_print_messages(message="file not exists : " + str(catalog_file),
                                                     doc=Doc.CONFIG)
            if not isinstance(lst, dict):
                ColorPrint.exit_after_print_messages(message="file not valid : " + str(catalog_file),
                                                     doc=Doc.CONFIG)
            StateHolder.catalogs[key] = lst

    @staticmethod
    def write_catalog(catalog):
        """Write catalog file"""
        if catalog is not None and catalog in StateHolder.catalogs:
            string_format = yaml.dump(data=StateHolder.catalogs[catalog], default_flow_style=False)
            StateHolder.catalog_repositories[catalog].repository.write_yaml_file(CatalogHandler.get_catalog_file(
                StateHolder.catalog_repositories[catalog].config), string_format)

    @staticmethod
    def set(modified):
        """Set project parameters and write, if it is exists"""
        for catalog in StateHolder.catalogs:
            if StateHolder.name in StateHolder.catalogs[catalog]:
                StateHolder.catalogs[catalog][StateHolder.name] = modified
            CatalogHandler.write_catalog(catalog)

    @staticmethod
    def add_to_list(name, url, file=None, repo_name=None):
        """Add project to the catalog"""
        catalog = StateHolder.args.get('<catalog>')
        if catalog is None:
            catalog = CatalogHandler.get_default_catalog()
        if catalog not in StateHolder.catalogs:
            ColorPrint.exit_after_print_messages(message="Catalog not exists : " + str(catalog))
        lst = StateHolder.catalogs[catalog]
        lst[name] = dict()
        lst[name]['git'] = str(url)  # later support svn
        if file is not None:
            lst[name]['file'] = file
        if repo_name is not None:
            lst[name]['repository_dir'] = repo_name
        CatalogHandler.write_catalog(catalog=catalog)

    @staticmethod
    def get_catalog_repository(catalog=None):
        if catalog is None:
            return StateHolder.default_catalog_repository.repository
        if catalog not in StateHolder.catalog_repositories:
            ColorPrint.exit_after_print_messages(message="Catalog not exists : " + str(catalog))
        else:
            return StateHolder.catalog_repositories[catalog].repository

    @staticmethod
    def get_repository(key, repo, silent=False):
        conf = StateHolder.config[key]
        if StateHolder.offline and repo in ('git', 'svn'):
            repository = FileRepository(target_dir=os.path.join(StateHolder.home_dir, 'catalogHome', key))
        elif 'git' == repo:
            repository = GitRepository(target_dir=os.path.join(StateHolder.home_dir, 'catalogHome', key),
                                       url=CatalogHandler.get_url(conf),
                                       branch=CatalogHandler.get_branch(conf),
                                       git_ssh_identity_file=conf.get("ssh-key"), silent=silent)
        elif 'svn' == repo:
            repository = SvnRepository(target_dir=os.path.join(StateHolder.home_dir, 'catalogHome', key),
                                       url=CatalogHandler.get_url(conf))
        elif 'github' == repo:
            repository = GitHubRepository(target_dir=os.path.join(StateHolder.home_dir, 'gitHub', key),
                                          tokenOrUser=conf.get("token", conf.get("user")), passw=conf.get("pass"),
                                          url=CatalogHandler.get_url(conf))
        elif 'gitlab' == repo:
            repository = GitLabRepository(target_dir=os.path.join(StateHolder.home_dir, 'gitLab', key),
                                          token=conf.get("token"),
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
            elif 'github' == config["repositoryType"]:
                return 'github'
            elif 'gitlab' == config["repositoryType"]:
                return 'gitlab'
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
            #  TODO backward compatibility
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
            CatalogHandler.check_and_print_project(lst)
        else:
            ColorPrint.print_with_lvl(
                message="Project catalog is empty. You can add projects with 'pocok repo add' command",
                lvl=-1)

    @staticmethod
    def check_and_print_project(lst):
        for cat in lst.keys():
            for key in lst[cat].keys():
                msg = key
                if os.path.exists(os.path.join(
                    StateHolder.work_dir,
                        lst[cat][msg]["repository_dir"] if "repository_dir" in lst[cat][msg] else msg)):
                    msg += " (*)"
                ColorPrint.print_with_lvl(message=msg, lvl=-1)


class CatalogData:
    def __init__(self, config, repository):
        self.config = config
        self.repository = repository

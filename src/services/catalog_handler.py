import os.path as path
import yaml
from .console_logger import *
from .file_repository import FileRepository
from .git_repository import GitRepository
from .svn_repository import SvnRepository


class CatalogHandler:

    def __init__(self, home_dir, repo_type, file=None, url=None, branch=None, ssh=None):
        self.catalog_file = file
        if 'git' == repo_type:
            self.catalog_repository = GitRepository(target_dir=path.join(home_dir, 'catalogHome'), url=url,
                                                    branch=branch, git_ssh_identity_file=ssh)
        elif 'svn' == repo_type:
            self.catalog_repository = SvnRepository(target_dir=path.join(home_dir, 'catalogHome'), url=url)
        else:
            self.catalog_repository = FileRepository(target_dir=home_dir)

    def get_catalog(self):
        """Parse catalog file"""
        lst = self.catalog_repository.get_yaml_file(file=self.catalog_file, create=True)
        if lst is None:
            ColorPrint.exit_after_print_messages(message="file not exists : " + str(self.catalog_file),
                                                 doc=Doc.CONFIG)
        if not isinstance(lst, dict):
            ColorPrint.exit_after_print_messages(message="file not valid : " + str(self.catalog_file),
                                                 doc=Doc.CONFIG)
        # TODO
        return lst

    def write_catalog(self, lst):
        """Write catalog file"""
        string_format = yaml.dump(data=lst, default_flow_style=False)
        self.catalog_repository.write_yaml_file(self.catalog_file, string_format)

    def get(self, name):
        """Get project parameters form catalog, if it is exists"""
        catalog = self.get_catalog()
        if name in catalog.keys():
            return catalog.get(name)
        ColorPrint.exit_after_print_messages(message="Project with name: %s not exist" % name)

    def set(self, name, modified):
        """Set project parameters and write, if it is exists"""
        catalog = self.get_catalog()
        if name in catalog.keys():
            catalog[name] = modified
            self.write_catalog(catalog)

    def add_to_list(self, name, handler, url, file=None, repo_name=None):
        """Add project to the catalog"""
        lst = self.get_catalog()
        lst[name] = dict()
        lst[name][handler] = str(url)
        if file is not None:
            lst[name]['file'] = file
        if repo_name is not None:
            lst[name]['repository_dir'] = repo_name
        self.write_catalog(lst)

    def remove_from_list(self, name):
        """Remove project from catalog"""
        lst = self.get_catalog()
        if name not in lst:
            ColorPrint.exit_after_print_messages(message="Project not exists in catalog: " + name)
        lst.pop(name)
        self.write_catalog(lst)

    def get_catalog_repository(self):
        return self.catalog_repository

    def push(self):
        self.catalog_repository.push()

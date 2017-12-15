import os
from .file_repository import FileRepository
from .git_repository import GitRepository
from .svn_repository import SvnRepository
from .state import StateHolder
from .console_logger import *


class ProjectUtils:

    def __init__(self):
        self.repositories = {}

    def get_project_repository(self, project_element, ssh):
        """Get and store repository handler for named project"""
        if StateHolder.offline:
            repo_handler = FileRepository(target_dir=self.get_target_dir(project_element=project_element))
        elif 'git' in project_element:
            branch = project_element.get('branch', 'master')
            repo_handler = GitRepository(target_dir=self.get_target_dir(project_element=project_element),
                                         url=project_element.get('git'), branch=branch,
                                         git_ssh_identity_file=ssh)
        elif 'svn' in project_element:
            repo_handler = SvnRepository(target_dir=self.get_target_dir(project_element=project_element),
                                         url=project_element.get('svn'))
        else:
            repo_handler = FileRepository(target_dir=self.get_target_dir(project_element=project_element))
        self.repositories[StateHolder.name] = repo_handler
        return repo_handler

    def add_repository(self, target_dir):

        repo_handler = FileRepository(target_dir=target_dir)
        self.repositories[StateHolder.name] = repo_handler
        return repo_handler

    def get_compose_file(self, project_element, ssh, silent=False):
        """Get compose file from project repository """

        if StateHolder.config is None:
            repository = self.add_repository(target_dir=StateHolder.work_dir)
            file = repository.get_file('poco.yml')
        else:
            repo_handler = self.get_project_repository(project_element=project_element, ssh=ssh)
            file = repo_handler.get_file(project_element.get('file', 'poco.yml'))
        if not os.path.exists(file):
            if silent:
                return None
            ColorPrint.exit_after_print_messages(
                message="Compose file : %s not exists in project : %s " % (str(file), str(StateHolder.name)),
                doc=Doc.POCO_CATALOG)
        return file

    def get_file(self, file):
        """Get file from project repository"""
        return self.repositories.get(StateHolder.name).get_file(file)

    @staticmethod
    def get_target_dir(project_element):
        return os.path.join(StateHolder.work_dir, project_element.get('repository_dir', StateHolder.name))

    @staticmethod
    def get_list_value(value):
        """Get list format, doesn't matter the config use one or list plan"""
        lst = list()
        if type(value) is list:
            lst.extend(value)
        else:
            lst.append(value)
        return lst


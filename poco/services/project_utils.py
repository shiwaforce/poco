import os
from .file_repository import FileRepository
from .git_repository import GitRepository
from .svn_repository import SvnRepository
from .console_logger import *


class ProjectUtils:

    def __init__(self, home_dir, work_dir, offline):
        self.home_dir = home_dir
        self.work_dir = work_dir
        self.offline = offline
        self.repositories = {}

    def get_project_repository(self, name, project_element, ssh):
        """Get and store repository handler for named project"""
        if self.offline:
            repo_handler = FileRepository(target_dir=self.get_target_dir(work_dir=self.work_dir, name=name,
                                                                         project_element=project_element))
        elif 'git' in project_element:
            branch = project_element.get('branch', 'master')
            repo_handler = GitRepository(target_dir=self.get_target_dir(work_dir=self.work_dir, name=name,
                                         project_element=project_element),
                                         url=project_element.get('git'), branch=branch,
                                         git_ssh_identity_file=ssh)
        elif 'svn' in project_element:
            repo_handler = SvnRepository(target_dir=self.get_target_dir(work_dir=self.work_dir, name=name,
                                         project_element=project_element),
                                         url=project_element.get('svn'))
        else:
            repo_handler = FileRepository(target_dir=self.get_target_dir(work_dir=self.work_dir, name=name,
                                          project_element=project_element))
        self.repositories[name] = repo_handler
        return repo_handler

    def get_compose_file(self, name, project_element, ssh, silent=False):
        """Get compose file from project repository """
        repo_handler = self.get_project_repository(name=name, project_element=project_element, ssh=ssh)
        file = repo_handler.get_file(project_element.get('file', 'poco.yml'))
        if not os.path.exists(file):
            if silent:
                return None
            ColorPrint.exit_after_print_messages(
                message="Compose file : %s not exists in project : %s " % (str(file), str(name)),
                doc=Doc.POCO_CATALOG)
        return file

    def get_file(self, name, file):
        """Get file from project repository"""
        return self.repositories.get(name).get_file(file)

    @staticmethod
    def get_target_dir(work_dir, name, project_element):
        return os.path.join(work_dir, project_element.get('repository_dir', name))


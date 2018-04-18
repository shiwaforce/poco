import os
from gitlab import Gitlab
from .abstract_repository import AbstractRepository
from .console_logger import ColorPrint


class GitLabRepository(AbstractRepository):

    gitlab = None

    def __init__(self, target_dir, token=None, url=None, silent=False):
        super(GitLabRepository, self).__init__(target_dir)

        target_url = url if url is not None else "http://gitlab.com"

        if token is None:
            ColorPrint.exit_after_print_messages(message="Gitlab configuration is empty!")
        else:
            self.gitlab = Gitlab(target_url, private_token=token)
            self.gitlab.version()  # test connection
            projects = self.gitlab.projects.list()
            for project in projects:
                print(project.name)

    def push(self):
        print("TODO")

    def pull(self):
        print("TODO")


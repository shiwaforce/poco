import os
import sys
import yaml
from github import Github, MainClass
from .abstract_repository import AbstractRepository
from .console_logger import ColorPrint
from .state import StateHolder


class GitHubRepository(AbstractRepository):

    github = None

    def __init__(self, name, token=None, user=None, passw=None, url=None):
        super(GitHubRepository, self).__init__(os.path.join(StateHolder.home_dir, 'gitHub', name))

        if sys.version_info[0] < 3:
            ColorPrint.exit_after_print_messages("Sorry, GitHub repository not supported with Python version below 3")

        url = url if url is not None else MainClass.DEFAULT_BASE_URL

        if token is None and user is None:
            ColorPrint.exit_after_print_messages(message="Github configuration is empty in section : " + name + "!")
        if token is not None:
            self.github = Github(token, base_url=url)
        else:
            self.github = Github(user, passw, base_url=url)

        user = self.github.get_user()  # check connection
        lst = dict()

        for repo in user.get_repos():
            repo_name = str(repo.name)
            lst[repo_name] = dict()
            lst[repo_name]['git'] = str(repo.clone_url)

        self.write_yaml_file(os.path.join(self.target_dir, 'poco-catalog.yml'),
                             yaml.dump(data=lst, default_flow_style=False), create=True)

    def push(self):
        print("TODO")

    def pull(self):
        print("TODO")

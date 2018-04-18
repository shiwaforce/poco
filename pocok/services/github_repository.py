import os
import yaml
from github import Github, MainClass
from .abstract_repository import AbstractRepository
from .console_logger import ColorPrint


class GitHubRepository(AbstractRepository):

    GITHUB_PREFIX = "github-"
    github = None

    def __init__(self, target_dir, tokenOrUser=None, passw=None, url=None, silent=False):
        super(GitHubRepository, self).__init__(target_dir)

        url = url if url is not None else MainClass.DEFAULT_BASE_URL

        if tokenOrUser is None:
            ColorPrint.exit_after_print_messages(message="Github configuration is empty!")
        if passw is None:
            self.github = Github(tokenOrUser, base_url=url)
        else:
            self.github = Github(tokenOrUser, passw, base_url=url)

        if self.github is None:
            ColorPrint.exit_after_print_messages("Github configuration is empty!")
        else:
            self.github.get_user()

        if url is None:
            ColorPrint.exit_after_print_messages(message="GIT URL is empty")

        lst = dict()

        for repo in self.github.get_user().get_repos():
            name = self.GITHUB_PREFIX + repo.name
            lst[name] = dict()
            lst[name]['git'] = str(repo.clone_url)

        self.write_yaml_file(os.path.join(target_dir, 'pocok-catalog.yml'),
                             yaml.dump(data=lst, default_flow_style=False))

    def push(self):
        print("TODO")

    def pull(self):
        print("TODO")


import os
import yaml
from gitlab import Gitlab
from .abstract_repository import AbstractRepository
from .console_logger import ColorPrint
from .state import StateHolder


class GitLabRepository(AbstractRepository):

    gitlab = None

    def __init__(self, name, token=None, url=None, ssh=None):
        super(GitLabRepository, self).__init__(os.path.join(StateHolder.home_dir, 'gitLab', name))

        target_url = url if url is not None else "http://gitlab.com"

        if token is None:
            ColorPrint.exit_after_print_messages(message="Gitlab configuration is empty in section " + name + "!")
        else:
            self.gitlab = Gitlab(target_url, private_token=token)
            self.gitlab.version()  # test connection

            self.process_projects(projects=self.gitlab.projects.list(membership=True), ssh=ssh)

    def process_projects(self, projects, ssh):
        lst = dict()
        for project in projects:
            project_name = str(project.name)
            lst[project_name] = dict()
            lst[project_name]['git'] = str(project.ssh_url_to_repo)
            if ssh is not None:
                lst[project_name]['ssh'] = ssh

        self.write_yaml_file(os.path.join(self.target_dir, 'poco-catalog.yml'),
                             yaml.dump(data=lst, default_flow_style=False), create=True)

    def push(self):
        print("TODO")

    def pull(self):
        print("TODO")

import os
import yaml
from gitlab import Gitlab
from .abstract_repository import AbstractRepository
from .console_logger import ColorPrint


class GitLabRepository(AbstractRepository):

    gitlab = None

    def __init__(self, target_dir, token=None, url=None, ssh=None):
        super(GitLabRepository, self).__init__(target_dir)

        target_url = url if url is not None else "http://gitlab.com"

        if token is None:
            ColorPrint.exit_after_print_messages(message="Gitlab configuration is empty!")
        else:
            self.gitlab = Gitlab(target_url, private_token=token)
            self.gitlab.version()  # test connection
            lst = dict()
            projects = self.gitlab.projects.list(membership=True)
            for project in projects:
                name = project.name
                lst[name] = dict()
                lst[name]['git'] = str(project.ssh_url_to_repo)
                if ssh is not None:
                    lst[name]['ssh'] = ssh

            self.write_yaml_file(os.path.join(target_dir, 'pocok-catalog.yml'),
                                 yaml.dump(data=lst, default_flow_style=False), create=True)

    def push(self):
        print("TODO")

    def pull(self):
        print("TODO")

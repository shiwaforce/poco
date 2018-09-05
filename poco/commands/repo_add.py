from .abstract_command import AbstractCommand
from ..services.config_handler import ConfigHandler
from ..services.state import StateHolder
from ..services.state_utils import StateUtils


class RepoAdd(AbstractCommand):

    sub_command = "repo"
    command = ["add", "modify"]
    args = ["<name>", "<git-url>", "[<branch>]", "[<file>]"]
    args_descriptions = {"<name>": "Name of the repository.",
                         "<git-url>": "URL of catalog's GIT repository",
                         "[<branch>]": "Name of the branch that should be checked out.(default: master)",
                         "[<file>]": "Name of the catalog file in the repository (default: proco-catalog.yml)."}
    description = "Run: 'poco repo add default https://github.com/shiwaforce/poco-example master' to add new " \
                  "catalog to the config from github and use master branch. Modify command use same metholody."

    def prepare_states(self):
        StateUtils.prepare("catalog_read")

    def resolve_dependencies(self):
        pass

    def execute(self):
        config = self.get_config_with_type('git', [('server', '<git-url>'), ('branch', '<branch>'), ('file', '<file>')])
        ConfigHandler.add(new_config=config)

    @staticmethod
    def get_config_with_type(repo_type, add_param):
        config = dict()
        config['repositoryType'] = repo_type
        for param in add_param:
            if StateHolder.has_args(param[1]):
                config[param[0]] = StateHolder.args.get(param[1])
        return config


class GitHubAdd(RepoAdd):

    sub_command = "github"
    args = ["<name>", "<login>", "[<url>]"]
    args_descriptions = {"<name>": "Name of the repository.",
                         "<login>": "Authentication data for GitHub account. Token or username/password.",
                         "[<url>]": "URL if you want to use your private GitHub server"}
    description = "Run: 'poco repo add github xxxxxxxx' to add your GitHub account. Afterwards you can list  " \
                  "your GitHub projects in catalog. Modify command use same metholody."

    def execute(self):
        config = self.get_config_with_type('github', [('server', '<url>')])
        login = StateHolder.args.get('<login>')
        if "/" in login:
            args = login.split("/")
            config['user'] = args[0]
            config['pass'] = args[1]
        else:
            config['token'] = login
        ConfigHandler.add(new_config=config)


class GitLabAdd(RepoAdd):

    sub_command = "gitlab"
    args = ["<name>", "<login>", "[<url>]", "[<ssh>]"]
    args_descriptions = {"<name>": "Name of the repository.",
                         "<login>": "Authentication data for GitLab account. It works with Token only.",
                         "[<url>]": "URL if you want to use your private GitLab server",
                         "[<ssh>]": "location of SSH key for your GitLab projects (default is '/~/.ssh/id_rsa')"}
    description = "Run: 'poco repo add gitlab xxxxxxxx' to add your GitLab account. Afterwards you can list  " \
                  "your GitLab projects in catalog. Modify command use same metholody."

    def execute(self):
        params = [('token', '<login>'), ('server', '<url>'), ('ssh', '<ssh>')]
        config = self.get_config_with_type('gitlab', params)
        ConfigHandler.add(new_config=config)


class BitbucketAdd(RepoAdd):

    sub_command = "bitbucket"
    args = ["<name>", "<login>", "[<url>]", "[<ssh>]"]
    args_descriptions = {"<name>": "Name of the repository.",
                         "<login>": "Authentication data for Bitbucket account. It works with user/password only.",
                         "<url>": "URL for your private Bitbucket server",
                         "[<ssh>]": "location of SSH key for your Bitbucket projects (default is '/~/.ssh/id_rsa')"}
    description = "Run: 'poco repo add bitbucket xxxxxxxx' to add your Bitbucket account. Afterwards you can list  " \
                  "your Bitbucket projects in catalog. Modify command use same metholody."

    def execute(self):
        params = [('server', '<url>'), ('ssh', '<ssh>')]
        config = self.get_config_with_type('bitbucket', params)
        args = StateHolder.args.get('<login>').split("/")
        config['user'] = args[0]
        config['pass'] = args[1]
        ConfigHandler.add(new_config=config)

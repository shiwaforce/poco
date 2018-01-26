import os
from .services.state import StateHolder
from .services.file_utils import FileUtils
from .services.console_logger import ColorPrint


class PocokProject:

    DEFAULT = """Pocok project commands
        Usage:
          pocok project add [<target-dir>] [<catalog>]
          pocok project init [<project>]
          pocok project ls
          pocok project remove <project>

        """

    ADD = """Usage:
      pocok project add [<target-dir>] [<catalog>]

        -h, --help

        Specific parameters:
            <target-dir>      Target directory that will be added to the catalog. Default is the current directory.
            <catalog>         Name of the catalog.

        Add directory to catalog.
    """

    INIT = """Usage:
      pocok project init [<name>]

        -h, --help

        Specific parameters:
          <name>         Name of the project that will be added to the catalog

        Create pocok.yml and docker-compose.yml to a project if aren't exists.
    """

    LS = """Usage:
      pocok project ls

        -h, --help

        List all projects from the catalog(s).
    """

    REMOVE = """Usage:
    pocok project remove <name>

        -h, --help

        Specific parameters:
            <name>       Name of the project that will be removed

        Remove project from the catalog.
    """

    command_dict = {
        'add': ADD,
        'ls': LS,
        'init': INIT,
        'remove': REMOVE
    }

    @staticmethod
    def handle():
        if StateHolder.has_args('add'):
            target_dir = FileUtils.get_normalized_dir(StateHolder.args.get('<target-dir>'))
            repo, repo_dir = FileUtils.get_git_repo(target_dir)
            file_prefix = ""
            repo_name = None
            if target_dir != repo_dir:
                file_prefix = FileUtils.get_relative_path(base_path=repo_dir, target_path=target_dir)
                repo_name = os.path.basename(repo_dir)
            if os.path.exists(file_prefix + "pocok.yaml"):
                file = file_prefix + "pocok.yaml"
            else:
                file = file_prefix + "pocok.yml"
            #self.add_to_list(name=os.path.basename(target_dir), handler="git",
            #                 catalog=StateHolder.args.get('<catalog>'),
            #                 url=repo.remotes.origin.url, file=file,
            #                 repo_name=repo_name)
            ColorPrint.print_info("Project added")
            return
        else:
            pass

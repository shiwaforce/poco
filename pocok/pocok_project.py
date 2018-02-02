import os
from .services.catalog_handler import CatalogHandler
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
            <target-dir>      Target directory that will be added to the catalog. (default: current directory)
            <catalog>         Name of the catalog. (default: name with default or first)

        Add directory to catalog.
    """

    INIT = """Usage:
      pocok project init [<project>]

        -h, --help

        Specific parameters:
          <project>         Name of the project that will be added to the catalog

        Create pocok.yml and docker-compose.yml to a project if aren't exists.
    """

    LS = """Usage:
      pocok project ls

        -h, --help

        List all projects from the catalog(s).
    """

    REMOVE = """Usage:
    pocok project remove <project>

        -h, --help

        Specific parameters:
            <project>       Name of the project that will be removed

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
            directory = None
            repo_name = None
            if target_dir != repo_dir:
                directory = FileUtils.get_relative_path(base_path=repo_dir, target_path=target_dir)
                repo_name = os.path.basename(repo_dir)
            file_name = FileUtils.get_backward_compatible_pocok_file(target_dir)
            file = file_name if directory is None else directory + file_name
            CatalogHandler.add_to_list(name=os.path.basename(target_dir), handler="git",
                                       catalog=StateHolder.args.get('<catalog>'),
                                       url=repo.remotes.origin.url, file=file, repo_name=repo_name)
            ColorPrint.print_info("Project added")
            return
        elif StateHolder.has_args('remove'):
            CatalogHandler.remove_from_list()
            ColorPrint.print_info("Project removed")
            return
        elif StateHolder.has_args('init'):
            pass

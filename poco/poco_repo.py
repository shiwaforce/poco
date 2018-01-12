from .services.state import StateHolder
from .services.console_logger import ColorPrint
from .services.catalog_handler import CatalogHandler


class PocoRepo:

    DEFAULT = """Poco repo commands
    Usage:
      poco repo (add|modify) <name> <git-url> [<branch>] [<file>]
      poco repo branch <branch> [<name>] [-f]
      poco repo branches [<name>]
      poco repo ls
      poco repo push [<name>]
      poco repo (remove|rm) <name>
    """
    LS = """Usage:
      poco repo ls

        -h, --help

        List the configs of repos.
    """

    ADD = """Usage:
      poco repo (add|modify) <name> <git-url> [<branch>] [<file>]

        -h, --help

        Specific parameters:
            <name>          Name of the repository.
            <git-url>       URL of catalog's GIT repository.
            <branch>        Name of the branch that should be checked out. (default : master)
            <file>          Name of the catalog file in the repository. (default: poco-catalog.yml)

        Add new/Modify repository to the config.
    """

    REMOVE = """Usage:
      poco repo (remove|rm) <name>

        -h, --help

        Specific parameters:
            <name>       Name of the catalog.

        Remove repository from local config.
    """

    BRANCH = """Usage:
        poco repo branch <branch> [<name>] [-f]

        -h, --help

        Specific parameters:
            <branch>        Name of the branch that should be checked out.
            <name>          Name of the catalog.
            -f              Force switch.

        Switch catalog branch if it is using GIT.
    """

    BRANCHES = """Usage:
        poco repo branches [<name>]

        -h, --help

        Specific parameters:
            <name>       Name of the catalog.

        List all available branches of catalog's GIT repository.
    """

    PUSH = """Usage:
        poco repo push [<name>]

        -h, --help

        Specific parameters:
            <name>       Name of the catalog.

        Push changes into catalog's remote GIT repository
    """

    command_dict = {
        'ls': LS,
        'add': ADD,
        'modify': ADD,
        'remove': REMOVE,
        'rm': REMOVE,
        'branch': BRANCH,
        'branches': BRANCHES,
        'push': PUSH
    }

    @staticmethod
    def handle():
        if StateHolder.config is None:
            ColorPrint.exit_after_print_messages('repo commands works only with config file.\n '
                                                 'Run "catalog init" command to create one.')
        StateHolder.catalog_handler = CatalogHandler()
        if StateHolder.has_args('remove'):
            if StateHolder.name in StateHolder.catalogs:
                pass
                #if self.get_compose_file(silent=True) is not None:
                #    self.init_compose_handler()
                #    CommandHandler(project_utils=self.project_utils).run_script("remove_script")
            StateHolder.catalog_handler.handle_command()
            return

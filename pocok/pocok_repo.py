from .services.state import StateHolder
from .services.console_logger import ColorPrint
from .services.catalog_handler import CatalogHandler
from .services.config_handler import ConfigHandler
from .services.file_utils import FileUtils


class PocokRepo:

    DEFAULT = """Pocok repo commands
    Usage:
      pocok repo (add|modify) <name> <git-url> [<branch>] [<file>]
      pocok repo branch <branch> [<name>] [-f]
      pocok repo branches [<name>]
      pocok repo ls
      pocok repo push [<name>]
      pocok repo (remove|rm) <name>
    """
    LS = """Usage:
      pocok repo ls

        -h, --help

        List the configs of repos.
    """

    ADD = """Usage:
      pocok repo (add|modify) <name> <git-url> [<branch>] [<file>]

        -h, --help

        Specific parameters:
            <name>          Name of the repository.
            <git-url>       URL of catalog's GIT repository
            <branch>        Name of the branch that should be checked out. (default : master)
            <file>          Name of the catalog file in the repository. (default: pocok-catalog.yml)

        Add new/Modify repository to the config.
    """

    REMOVE = """Usage:
      pocok repo (remove|rm) <name>

        -h, --help

        Specific parameters:
            <name>       Name of the catalog.

        Remove repository from local config.
    """

    BRANCH = """Usage:
        pocok repo branch <branch> [<name>] [-f]

        -h, --help

        Specific parameters:
            <branch>        Name of the branch that should be checked out.
            <name>          Name of the catalog.
            -f              Force switch.

        Switch catalog branch if it is using GIT.
    """

    BRANCHES = """Usage:
        pocok repo branches [<name>]

        -h, --help

        Specific parameters:
            <name>       Name of the catalog.

        List all available branches of catalog's GIT repository.
    """

    PUSH = """Usage:
        pocok repo push [<name>]

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
        if StateHolder.has_args('ls'):
            ColorPrint.exit_after_print_messages(message=ConfigHandler.print_config(), msg_type="info")
            return
        elif StateHolder.has_least_one_arg('add', 'modify'):
            ConfigHandler.add()
            return
        if StateHolder.config is None:
            ColorPrint.exit_after_print_messages('repo commands works only with config file.\n '
                                                 'Run "catalog init" command to create one.')
        if StateHolder.default_catalog_repository is None:
            CatalogHandler.load()

        if StateHolder.has_least_one_arg('remove', 'rm'):
            if StateHolder.name in StateHolder.catalogs:
                # TODO remove script
                #if self.get_compose_file(silent=True) is not None:
                #    self.init_compose_handler()
                #    CommandHandler(project_utils=self.project_utils).run_script("remove_script")
                pass
            ConfigHandler.remove()
            return

        if StateHolder.has_args('branch'):
            ConfigHandler.set_branch(StateHolder.args.get('<branch>'), StateHolder.args.get('<name>'))
            ColorPrint.print_info("Branch changed")
        elif StateHolder.has_least_one_arg('branches', 'push'):
            repository = CatalogHandler.get_catalog_repository(StateHolder.args.get('<name>'))
            if StateHolder.has_args('branches'):
                repository.print_branches()
            else:
                repository.push()
                ColorPrint.print_info("Push completed")

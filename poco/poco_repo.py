

class PocoRepo:

    DEFAULT = """Poco repo commands
    Usage:
      poco repo add <name> <git-url> [<branch>] [<file>]
      poco repo branch <branch> [<name>] [-f]
      poco repo branches [<name>]
      poco repo init
      poco repo ls
      poco repo push [<name>]
      poco repo (remove|rm) <name>
    """

    INIT = """Usage:
      poco repo init

        -h, --help

        Initialize default environment and an sample catalog.
    """

    LS = """Usage:
      poco repo ls

        -h, --help

        List the configs of catalogs.
    """

    ADD = """Usage:
      poco repo (add|modify) <name> <git-url> [<branch>] [<file>]

        -h, --help

        Specific parameters:
            <name>       Name of the catalogue.
            <git-url>       URL of catalog's GIT repository.
            <branch>        Name of the branch that should be checked out. (default : master)
            <file>          Name of the catalog file in the repository. (default: poco-catalog.yml)

        Add/Modify new catalog to the config.
    """

    REMOVE = """Usage:
      poco repo (remove|rm) <name>

        -h, --help

        Specific parameters:
            <name>       Name of the catalog.

        Remove catalog from local config.
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
            <name>       Name of the catalogue.

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
        'init': INIT,
        'ls': LS,
        'add': ADD,
        'modify': ADD,
        'remove': REMOVE,
        'rm': REMOVE,
        'branch': BRANCH,
        'branches': BRANCHES,
        'push': PUSH
    }

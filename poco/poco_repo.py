

class PocoRepo:

    DEFAULT = """Poco repo commands
    Usage:
      poco repo add <catalog> <git-url> [<branch>] [<file>]
      poco repo branch <branch> [<catalog>] [-f]
      poco repo branches [<catalog>]
      poco repo init
      poco repo ls
      poco repo push [<catalog>]
      poco repo (remove|rm) <catalog>
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
      poco repo add <catalog> <git-url> [<branch>] [<file>]

        -h, --help

        Specific parameters:
            <catalog>       Name of the catalogue.
            <git-url>       URL of catalog's GIT repository.
            <branch>        Name of the branch that should be checked out. (default : master)
            <file>          Name of the catalog file in the repository. (default: poco-catalog.yml)

        Add new catalog to the config.
    """

    REMOVE = """Usage:
      poco repo (remove|rm) <catalog>

        -h, --help

        Specific parameters:
            <catalog>       Name of the catalog.

        Remove catalog from local config.
    """

    BRANCH = """Usage:
        poco repo branch <branch> [<catalog>] [-f]

        -h, --help

        Specific parameters:
            <branch>        Name of the that should be checked out.
            <catalog>       Name of the catalog.
            -f              Force switch.

        Switch catalog branch if it is using GIT.
    """

    BRANCHES = """Usage:
        poco repo branches [<catalog>]

        -h, --help

        Specific parameters:
            <catalog>       Name of the catalog.

        List all available branches of catalog's GIT repository.
    """

    PUSH = """Usage:
        poco repo push [<catalog>]

        -h, --help

        Specific parameters:
            <catalog>       Name of the catalog.

        Push changes into catalog's remote GIT repository
    """

    command_dict = {
        'init': INIT,
        'ls': LS,
        'add': ADD,
        'remove': REMOVE,
        'rm': REMOVE,
        'branch': BRANCH,
        'branches': BRANCHES,
        'push': PUSH
    }

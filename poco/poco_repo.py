

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

        Initalize default environment and an sample catalogue.
    """

    LS = """Usage:
      poco repo ls

        -h, --help

        List the configs of catalogues.
    """

    ADD = """Usage:
      poco repo add <catalog> <git-url> [<branch>] [<file>]

        -h, --help

        Specific parameters:
            <catalog>       Name of the catalogue.
            <git-url>       URL for catalogue's GIT repository.
            <branch>        Name of the branch what we want to set. (default : master)
            <file>          Name of the catalogue file in the repository. (default: poco-catalog.yml)

        Add new catalogue to the config.
    """

    REMOVE = """Usage:
      poco repo (remove|rm) <catalog>

        -h, --help

        Specific parameters:
            <catalog>       Name of the catalogue.

        Remove catalogue from local config.
    """

    BRANCH = """Usage:
        poco repo branch <branch> [<catalog>] [-f]

        -h, --help

        Specific parameters:
            <branch>        Name of the branch what we want to set.
            <catalog>       Name of the catalogue.
            -f              Force switch.

        Switch catalogue branch if its using GIT.
    """

    BRANCHES = """Usage:
        poco repo branches [<catalog>]

        -h, --help

        Specific parameters:
            <catalog>       Name of the catalogue.

        List all available branch in catalogue's GIT repository.
    """

    PUSH = """Usage:
        poco repo push [<catalog>]

        -h, --help

        Specific parameters:
            <catalog>       Name of the catalogue.

        Push changes into catalogue's remote GIT repository
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

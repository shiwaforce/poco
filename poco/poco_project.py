
class PocoProject:

    DEFAULT = """Poco project commands
        Usage:
          poco project add [<target-dir>] [<catalog>]
          poco project ls
          poco project remove <project>

        """

    ADD = """Usage:
      poco project add [<target-dir>] [<catalog>]

        -h, --help

        Specific parameters:
            <target-dir>      Target directory that will be added to the catalog. Default is the current directory.
            <catalog>         Name of the catalog.

        Add directory to catalog.
    """

    INIT = """Usage:
      poco project init [<project>]

        -h, --help

        Specific parameters:
          <project>         Name of the project that will be added to the catalog

        Create poco.yml and docker-compose.yml to a project if aren't exists.
    """

    LS = """Usage:
      poco project ls

        -h, --help

        List all projects from the catalog(s).
    """

    REMOVE = """Usage:
    poco project remove <project>

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


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
            <target-dir>      Directory that be added to catalogue. Default is the actual directory.
            <catalog>         Name of the catalogue.

        Add directory to catalogue.
    """

    INIT = """Usage:
      poco project init [<project>]

        -h, --help

        Specific parameters:
          <project>         Name of the project in the catalog

        Create poco.yml and docker-compose.yml to a project if aren't exists.
    """

    LS = """Usage:
      poco project ls

        -h, --help

        List all projects from catalogue(s).
    """

    REMOVE = """Usage:
    poco project remove <project>

        -h, --help

        Specific parameters:
            <project>       Name of the projects what want to remove.

        Remove project from catalogue.
    """

    command_dict = {
        'add': ADD,
        'ls': LS,
        'init': INIT,
        'remove': REMOVE
    }

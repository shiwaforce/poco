
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
        pass

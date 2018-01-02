

class PocoCatalog:

    CATALOG = """Usage:
      poco catalog add [<target-dir>] [<catalog>]
      poco catalog init
      poco catalog ls
      poco catalog branch <branch> [<catalog>] [-f]
      poco catalog branches [<catalog>]
      poco catalog push [<catalog>]
      poco catalog remove [<project>]

    """

    ADD = """Usage:
      poco catalog add [<target-dir>] [<catalog>]

        -h, --help

        Specific parameters:
            <target-dir>      Directory that be added to catalogue. Default is the actual directory.
            <catalog>         Name of the catalogue.

        Add directory to catalogue.
    """

    INIT = """Usage:
      poco catalog init

        -h, --help

        Add directory to catalogue.
    """

    command_dict = {
        'catalog': CATALOG,
        'add': ADD,

    }

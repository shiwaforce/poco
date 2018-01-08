
class PocoCatalog:

    DEFAULT = """Poco catalog commands
    Usage:
      poco catalog init
      poco catalog ls

    """

    INIT = """Usage:
      poco catalog init

        -h, --help

        Initalize default environment and an sample catalogue.
    """

    LS = """Usage:
      poco catalog ls

        -h, --help

        List the available projects in catalogues.
    """

    command_dict = {
        'init': INIT,
        'ls': LS
    }
from .services.state import StateHolder


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

    @staticmethod
    def handle():
        if StateHolder.has_args('init'):
            StateHolder.config_handler.handle_command()
            return

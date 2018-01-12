from .services.state import StateHolder


class PocokCatalog:

    DEFAULT = """Pocok catalog commands
    Usage:
      pocok catalog init
      pocok catalog ls

    """

    INIT = """Usage:
      pocok catalog init

        -h, --help

        Initalize default environment and an sample catalogue.
    """

    LS = """Usage:
      pocok catalog ls

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

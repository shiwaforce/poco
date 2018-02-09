import os
from .services.catalog_handler import CatalogHandler
from .services.state import StateHolder
from .services.file_utils import FileUtils
from .services.console_logger import ColorPrint


class PocokProject:

    DEFAULT = """Pocok project commands
        Usage:
          pocok project add [<target-dir>] [<catalog>]
          pocok project init [<project>]
          pocok project ls
          pocok project (remove|rm) <project>

        """

    INIT = """Usage:
      pocok project init [<project>]

        -h, --help

        Specific parameters:
          <project>         Name of the project or the actual directory if it is empty

        Initialize pocok project, pocok.yml and docker-compose.yml will be created if they don't exist.
    """

    LS = """Usage:
      pocok project ls

        -h, --help

        List all projects from the catalog(s).
    """

    command_dict = {
        'ls': LS,
        'init': INIT
    }


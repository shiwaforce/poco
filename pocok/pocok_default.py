from .services.console_logger import ColorPrint
from .services.state import StateHolder
from .services.cta_utils import CTAUtils
from .services.catalog_handler import CatalogHandler


class PocokDefault:

    PROJECT_CONFIG = """Usage:
  pocok config [<project/plan>]

    -h, --help

    Specific parameters:
      <project/plan>         Name of the project in the catalog and/or name of the project's plan

    Print full Docker compose configuration for a project's plan.
"""
    CATALOG = """Usage:
  pocok catalog

    -h, --help

    List the available projects in repos.
"""

    CLEAN = """Usage:
  pocok clean

    -h, --help

    Clean all containers and images from the local Docker repository.
"""

    INIT = """Usage:
  pocok init [<project>]

    -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog

    Initialize pocok project, pocok.yml and docker-compose.yml will be created if they don't exist.
"""

    INSTALL = """Usage:
  pocok install [<project/plan>]

    -h, --help

    Specific parameters:
      <project/plan>         Name of the project in the catalog and/or name of the project's plan

    Clone projects from a remote repository, run install scripts.
"""

    START = """Usage:
  pocok (start|up) [<project/plan>]

  -h, --help

    Specific parameters:
      <project/plan>         Name of the project in the catalog and/or name of the project's plan

    Start pocok project with the default or defined plan.
"""
    STOP = """Usage:
  pocok (stop|down) [<project/plan>]

  -h, --help

    Specific parameters:
      <project/plan>         Name of the project in the catalog and/or name of the project's plan

    Stop project with the default or defined plan.
"""
    RESTART = """Usage:
  pocok restart [<project/plan>]

  -h, --help

    Specific parameters:
      <project/plan>         Name of the project in the catalog and/or name of the project's plan

    Restart project with the default or defined plan.
"""
    LOG = """Usage:
  pocok (log|logs) [<project/plan>]

  -h, --help

    Specific parameters:
      <project/plan>         Name of the project in the catalog and/or name of the project's plan

    Print docker containers logs of the current project with the default or defined plan.
"""
    BUILD = """Usage:
  pocok build [<project/plan>]

  -h, --help

    Specific parameters:
      <project/plan>         Name of the project in the catalog and/or name of the project's plan

    Build containers depends defined project and plan.
"""
    PS = """Usage:
  pocok ps [<project/plan>]

  -h, --help

    Specific parameters:
      <project/plan>         Name of the project in the catalog and/or name of the project's plan

    Print containers statuses which depends defined project and plan.
"""

    PLAN = """Usage:
  pocok plan ls [<project>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog

    Print all available plans of the project.
"""

    PULL = """Usage:
  pocok pull [<project/plan>]

  -h, --help

    Specific parameters:
      <project/plan>         Name of the project in the catalog and/or name of the project's plan

    Pull all necessary images for the project with the defined or default plan.
"""

    BRANCH = """Usage:
  pocok branch <project> <branch> [-f]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <branch>          Name of the git branch
      -f                Git force parameter

    Switch branch on a defined project.
"""
    BRANCHES = """Usage:
  pocok branches [<project>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog

    List all available git branches of the project.
"""
    PACK = """Usage:
  pocok pack [<project/plan>]

  -h, --help

    Specific parameters:
      <project/plan>         Name of the project in the catalog and/or name of the project's plan

    Pack the selected project's plan configuration with docker images into an archive.
"""

    UNPACK = """Usage:
  pocok unpack [<project>]

  -h, --help

    Unpack archive, install images to local repository.
"""

    command_dict = {
        'config': PROJECT_CONFIG,
        'catalog': CATALOG,
        'clean': CLEAN,
        'init': INIT,
        'install': INSTALL,
        'up': START,
        'down': STOP,
        'build': BUILD,
        'ps': PS,
        'plan': PLAN,
        'pull': PULL,
        'restart': RESTART,
        'start': START,
        'stop': STOP,
        'log': LOG,
        'logs': LOG,
        'branch': BRANCH,
        'branches': BRANCHES,
        'pack': PACK,
        'unpack': UNPACK
    }

    @staticmethod
    def handle():
        if StateHolder.has_args('catalog'):
            if StateHolder.catalog_handler is None:
                ColorPrint.print_warning("You have not catalog yet.", lvl=-1)
                ColorPrint.exit_after_print_messages(message=CTAUtils.CTA_STRINGS['default'], msg_type="info")
            else:
                CatalogHandler.print_ls()
            return

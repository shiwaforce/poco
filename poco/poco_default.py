
class PocoDefault:

    PROJECT_CONFIG = """Usage:
  poco project-config [<project>] [<plan>]

    -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the project's plan

    Print full Docker compose configuration for a project's plan.
"""
    CLEAN = """Usage:
  poco clean

    -h, --help

    Clean all containers and images from the local Docker repository.
"""

    INIT = """Usage:
  poco init [<project>]

    -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog

    Initialize poco project, poco.yml and docker-compose.yml will be created if they don't exist.
"""

    INSTALL = """Usage:
  poco install [<project>] [<plan>]

    -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the project's plan

    Clone projects from a remote repository, run install scripts.
"""

    START = """Usage:
  poco (start|up) [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the project's plan

    Start poco project with the default or defined plan.
"""
    STOP = """Usage:
  poco (stop|down) [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the project's plan

    Stop project with the default or defined plan.
"""
    RESTART = """Usage:
  poco restart [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the project's plan

    Restart project with the default or defined plan.
"""
    LOG = """Usage:
  poco (log|logs) [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the project's plan

    Print docker containers logs of the current project with the default or defined plan.
"""
    BUILD = """Usage:
  poco build [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the project's plan

    Build containers depends defined project and plan.
"""
    PS = """Usage:
  poco ps [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the project's plan

    Print containers statuses which depends defined project and plan.
"""

    PLAN = """Usage:
  poco plan ls [<project>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog

    Print all available plans of the project.
"""

    PULL = """Usage:
  poco pull [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the project's plan

    Pull all necessary images for the project with the defined or default plan.
"""

    BRANCH = """Usage:
  poco branch <project> <branch> [-f]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <branch>          Name of the git branch
      -f                Git force parameter

    Switch branch on a defined project.
"""
    BRANCHES = """Usage:
  poco branches [<project>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog

    List all available git branches of the project.
"""
    PACK = """Usage:
  poco pack [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the project's plan

    Pack the selected project's plan configuration with docker images into an archive.
"""

    UNPACK = """Usage:
  poco unpack [<project>]

  -h, --help

    Unpack archive, install images to local repository.
"""

    command_dict = {
        'project-config': PROJECT_CONFIG,
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

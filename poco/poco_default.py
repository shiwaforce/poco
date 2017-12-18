
class PocoDefault:

    PROJECT_CONFIG="""Usage:
  poco project-config [<project>] [<plan>]

    -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the plan in the project

    Print full Docker compose configuration for a project's plan.
"""
    CLEAN = """Usage:
  poco clean

    -h, --help

    Clean all container and image from local Docker repository.
"""

    INIT = """Usage:
  poco init [<project>]

    -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog

    Create poco.yml and docker-compose.yml to a project if aren't exists.
"""

    INSTALL = """Usage:
  poco init [<project>] [<plan>]

    -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the plan in the project

    Get projects from remote repository (if its not exists locally yet) and run install scripts.
"""

    START = """Usage:
  poco (start|up) [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the plan in the project

    Starts project with defined plan (or default/first)
"""
    STOP = """Usage:
  poco (stop|down) [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the plan in the project

    Stop project with defined plan (or default/first)
"""
    RESTART = """Usage:
  poco restart [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the plan in the project

    Restart project with defined plan (or default/first)
"""
    LOG = """Usage:
  poco (log|logs) [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the plan in the project

    Print containers logs which depends defined project and plan
"""
    BUILD = """Usage:
  poco build [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the plan in the project

    Build containers depends defined project and plan
"""
    PS = """Usage:
  poco ps [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the plan in the project

    Print containers statuses which depends defined project and plan
"""

    PLAN = """Usage:
  poco plan ls [<project>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog

    Print all available plan for the project
"""

    PULL = """Usage:
  poco pull [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the plan in the project

    Pull all necessary image for project and plan.
"""

    BRANCH = """Usage:
  poco branch <project> <branch> [-f]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <branch>          Name of the git branch
      -f                Git force parameter

    Switch branch on defined project.
"""
    BRANCHES = """Usage:
  poco branches [<project>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog

    List all available git branch for the project.
"""
    PACK = """Usage:
  poco pack [<project>] [<plan>]

  -h, --help

    Specific parameters:
      <project>         Name of the project in the catalog
      <plan>            Name of the plan in the project

    Pack the selected project's plan configuration with docker images to an archive.
"""

    UNPACK = """Usage:
  poco branches [<project>]

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

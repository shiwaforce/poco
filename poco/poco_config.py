

class PocoConfig:

    CONFIG = """Usage:
      poco config add <catalog> <git-url> [<branch>] [<file>]
      poco config
      poco config remove <catalog>

    """

    command_dict = {
        'config': CONFIG
    }

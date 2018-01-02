

class PocoConfig:

    CONFIG = """Usage:
      poco repo add <catalog> <git-url> [<branch>] [<file>]
      poco repo
      poco repo ls
      poco repo (remove|rm) <catalog>

    """

    command_dict = {
        'config': CONFIG
    }

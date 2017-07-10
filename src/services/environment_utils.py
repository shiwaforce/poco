import os


class EnvironmentUtils:

    @staticmethod
    def get_variable(key, default=None):
        return os.environ.get(key, default)

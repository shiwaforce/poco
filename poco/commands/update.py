from poco.services.environment_utils import EnvironmentUtils
from poco.services.state import StateHolder
from .abstract_command import AbstractCommand
from poco.poco import __version__

class Update(AbstractCommand):

    command = "getupdate"
    args = None
    args_descriptions = {}
    description = "Run: 'poco getupdate' to check for poco updates."

    def prepare_states(self):
        pass

    def resolve_dependencies(self):
        pass

    def execute(self):
        EnvironmentUtils.check_version(__version__, StateHolder.is_beta_tester, True)

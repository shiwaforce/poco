import abc
from ..services.console_logger import ColorPrint


class AbstractCommand(object):
    __metaclass__ = abc.ABCMeta

    sub_command = None
    command = None
    args = None
    description = None

    def __init__(self):
        self.prepared_states = False
        self.resolved_dependencies = False
        self.executed = False

    @abc.abstractmethod
    def prepare_states(self):
        ColorPrint.print_info("Abstract prepare states")
        return

    @abc.abstractmethod
    def resolve_dependencies(self):
        ColorPrint.print_info("Abstract resolve dependencies")
        return

    @abc.abstractmethod
    def execute(self):
        ColorPrint.print_info("Abstract execute")
        return

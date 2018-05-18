import abc
from ..services.console_logger import ColorPrint


class AbstractCommand(object):
    __metaclass__ = abc.ABCMeta

    sub_command = None
    command = None
    args = None
    description = None

    def __init__(self):
        self.state = CommandState.INIT

    @abc.abstractmethod
    def prepare_states(self):
        ColorPrint.print_info("Abstract prepare states")

    @abc.abstractmethod
    def resolve_dependencies(self):
        ColorPrint.print_info("Abstract resolve dependencies")

    @abc.abstractmethod
    def execute(self):
        ColorPrint.print_info("Abstract execute")

    def cleanup(self):
        pass


class CommandState:
    INIT = 1
    RESOLVE = 2
    EXECUTE = 3
    CLEANUP = 4
    DESTROYED = 5

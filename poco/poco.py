#!/usr/bin/env python
"""POCO - project compose.

Usage:
  poco [options] <command> [<args>...]


Options:
  --version         Print version of POCO
  -h --help         Show this screen.
  -v --verbose      Print more text.
  -q --quiet        Print less text.
  --always-update   Project repository handle by user
  --offline         Offline mode

The available poco commands are:
"""
import inspect
import importlib
import pkgutil
import os
import sys
from docopt import docopt
from .commands.abstract_command import AbstractCommand, CommandState
from .services.cta_utils import CTAUtils
from .services.environment_utils import EnvironmentUtils
from .services.console_logger import ColorPrint
from .services.state import StateHolder


END_STRING = """See 'poco help <command>' for more information on a specific command."""
__version__ = '0.96.4'


class Poco(object):

    command_classes = dict()
    active_object = None

    def __init__(self, home_dir=os.path.join(os.path.expanduser(path='~'), '.poco'),
                 argv=sys.argv[1:]):
        EnvironmentUtils.check_version(__version__)

        StateHolder.home_dir = home_dir
        self.argv = argv
        self.collect_commands()

    def start_flow(self):

        """PHASE ZERO - validate command """
        self.check_command()

        counter = 0
        if self.active_object is None:
            ColorPrint.exit_after_print_messages("Something went wrong. Command class not found for command: " +
                                                 sys.argv[1:])

        while counter < 10:  # for tests
            counter += 1

            if self.inner_flow():
                break

        if not counter < 10:
            ColorPrint.exit_after_print_messages("Can't complete the command running. States: \n"
                                                 "\tPrepare states: " + str(self.active_object.prepared_states) +
                                                 "\tResolve dependencies: " +
                                                 str(self.active_object.resolved_dependencies) +
                                                 "\tExecuted: " + str(self.active_object.executed))

    def inner_flow(self):
        cmd = self.active_object
        if cmd.state == CommandState.INIT:
            cmd.state = self.next_state(cmd.prepare_states(), CommandState.RESOLVE)
        elif cmd.state == CommandState.RESOLVE:
            cmd.state = self.next_state(cmd.resolve_dependencies(), CommandState.EXECUTE)
        elif cmd.state == CommandState.EXECUTE:
            cmd.state = self.next_state(cmd.execute(), CommandState.CLEANUP)
        elif cmd.state == CommandState.CLEANUP:
            cmd.state = self.next_state(cmd.cleanup(), CommandState.DESTROYED)
        elif cmd.state == CommandState.DESTROYED:
            return True

    @staticmethod
    def next_state(desired_next, default_next):
        if desired_next is None:
            return default_next
        return desired_next

    def check_command(self):
        if len(self.argv) == 0:
            self.argv.append('-h')
        StateHolder.args = docopt(self.get_full_doc(), version=__version__, options_first=True, argv=self.argv)
        StateHolder.args.update(self.command_interpreter(command=StateHolder.args['<command>'],
                                                         argv=[] + StateHolder.args['<args>']))
        ColorPrint.set_log_level(StateHolder.args)
        ColorPrint.print_info('arguments:\n' + str(StateHolder.args), 1)
        StateHolder.offline = StateHolder.has_args("--offline")
        StateHolder.always_update = StateHolder.has_args("--always-update")

    def get_full_doc(self):
        doc = __doc__
        commands = []
        for sub_cmd in self.command_classes.keys():
            if sub_cmd is None:
                [Poco.build_command(commands=commands, cls=cls) for cls in self.command_classes[None]]
                continue
            sub = "  " + sub_cmd + " [<subcommand>]"
            doc += sub + (42-len(sub)) * " " + "See 'poco help " + sub_cmd + "' for more.\n"
        doc += "".join(commands) + "\n" + END_STRING
        return doc

    def command_interpreter(self, command, argv):
        if command == 'help':
            argv.append('-h')
            if len(argv) == 1:
                docopt(self.get_full_doc() + "\n" + CTAUtils.get_cta(), argv=argv)
            self.command_interpreter(argv[0], argv[1:])
        if command in self.command_classes.keys():
            if len(argv) == 0:
                argv.append("-h")
            args = self.get_args(command=command, classes=self.command_classes[command], argv=argv)
            if args is None:
                docopt(self.build_sub_commands_help(command, classes=self.command_classes[command]),
                       argv=[command] + argv)
        else:
            args = self.get_args(command=None, classes=self.command_classes[None], argv=[command] + argv)
            if args is None:
                ColorPrint.exit_after_print_messages("%r is not a poco command. See 'poco help'." % command)
        return args

    @staticmethod
    def build_command(commands, cls):
        sub_command = getattr(cls, 'sub_command')
        command = getattr(cls, 'command')
        description = getattr(cls, 'description')

        if command is None:
            ColorPrint.print_info("Command class not contains command: " + str(cls), lvl=1)
            return
        if isinstance(command, list):
            cmd = "(" + "|".join(command) + ")"
        else:
            cmd = command
        if sub_command is not None:
            cmd = "poco " + sub_command + " " + cmd
        cmd += (40 - len(cmd)) * " "
        commands.append("  " + cmd + description + "\n")

    def get_args(self, command, classes, argv):
        for cls in classes:
            cmd = getattr(cls, 'command')
            if not isinstance(cmd, list):
                cmd = [cmd]
            if argv[0] in cmd:
                self.active_object = cls()
                return docopt(Poco.build_command_help(cls), argv=[command] + argv if command is not None else argv)

    @staticmethod
    def build_command_help(cls):
        sub_command = getattr(cls, 'sub_command')
        cmd = getattr(cls, 'command')
        if isinstance(cmd, list):
            cmd = "(" + "|".join(cmd) + ")"
        if sub_command is not None:
            cmd = sub_command + " " + cmd
        args = getattr(cls, 'args')
        desc = getattr(cls, 'description')
        doc = "Usage:\n  poco " + cmd
        if args is not None:
            doc += " " + " ".join(args)
        doc += "\n\n  -h, --help"
        if args is not None:
            Poco.build_command_help_from_args(cls=cls, doc=doc, args=args)
        doc += "\n  " + desc
        return doc

    @staticmethod
    def build_command_help_from_args(cls, doc, args):
        descriptions = getattr(cls, 'args_descriptions')
        doc += "\n\n  Specific parameters:\n"
        for arg in args:
            des = descriptions[arg] if arg in descriptions else " "
            doc += "    " + arg + (40 - len(arg)) * " " + des + "\n"

    @staticmethod
    def build_sub_commands_help(sub_command, classes):
        doc = "Poco " + sub_command + " commands\n\nUsage:\n"
        commands = []
        [Poco.build_command(commands=commands, cls=cls) for cls in classes]
        return doc + "".join(commands)

    def collect_commands(self):
        try:
            command_packages = importlib.import_module('poco.commands', package='poco')
            for importer, modname, ispkg in pkgutil.iter_modules(command_packages.__path__):
                if not ispkg:
                    mod = importlib.import_module('poco.commands.' + modname, 'poco')
                    for name, cls in inspect.getmembers(mod,
                                                        lambda member: inspect.isclass(member) and
                                                        member.__module__ == mod.__name__):
                        self.check_base_class(cls)
        except ImportError as ex:
            ColorPrint.exit_after_print_messages("Commands import error: " + str(ex.args))

    def check_base_class(self, cls):
        for base_class in inspect.getmro(cls)[1:]:
            if base_class == AbstractCommand:
                sub_command = getattr(cls, 'sub_command')
                if sub_command not in self.command_classes.keys():
                    self.command_classes[sub_command] = list()
                self.command_classes[sub_command].append(cls)
                break


def main():
    poco = Poco()
    try:
        poco.start_flow()
    except Exception as ex:
        if ColorPrint.log_lvl > 0:
            ColorPrint.exit_after_print_messages(message="Unexpected error: " + type(ex).__name__ + "\n" + str(ex))
        else:
            ColorPrint.exit_after_print_messages(message="Unexpected error: " + type(ex).__name__ + "\n" + str(ex.args)
                                                         + "\nRun with '-v' for more information.")

if __name__ == '__main__':
    sys.exit(main())

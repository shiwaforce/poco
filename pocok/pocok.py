#!/usr/bin/env python
"""Pocok project compose.

Usage:
  pocok [options] <command> [<args>...]


Options:
  --version         Print version of Pocok
  -h --help         Show this screen.
  -v --verbose      Print more text.
  -q --quiet        Print less text.
  --always-update   Project repository handle by user
  --offline         Offline mode

The available pocok commands are:
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


END_STRING = """See 'pocok help <command>' for more information on a specific command."""
__version__ = '0.24.0'


class Pocok(object):

    command_classes = dict()
    active_object = None

    def __init__(self, home_dir=os.path.join(os.path.expanduser(path='~'), '.pocok'),
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
            ColorPrint.exit_after_print_messages("Something went wrong. Command class not found for command: "
                                                 + sys.argv[1:])

        while counter < 10:  # for tests
            counter += 1

            cmd = self.active_object;

            if cmd.state == CommandState.INIT:
                cmd.state = self.next_state(cmd.prepare_states(), CommandState.RESOLVE)
            elif cmd.state == CommandState.RESOLVE:
                cmd.state = self.next_state(cmd.resolve_dependencies(), CommandState.EXECUTE)
            elif cmd.state == CommandState.EXECUTE:
                cmd.state = self.next_state(cmd.execute(), CommandState.CLEANUP)
            elif cmd.state == CommandState.CLEANUP:
                cmd.state = self.next_state(cmd.cleanup(), CommandState.DESTROYED)
            elif cmd.state == CommandState.DESTROYED:
                break;

        if not counter < 10:
            ColorPrint.exit_after_print_messages("Can't complete the command running. States: \n"
                                                 "\tPrepare states: " + str(self.active_object.prepared_states) +
                                                 "\tResolve dependencies: "
                                                 + str(self.active_object.resolved_dependencies) +
                                                 "\tExecuted: " + str(self.active_object.executed))

    def next_state(self, desired_next, default_next):
        if desired_next is None:
            return default_next
        return desired_next

    def check_command(self):
        argv = Pocok.handle_alternatives(self.argv)  # TODO move to new structure
        if len(argv) == 0:
            argv.append('-h')
        StateHolder.args = docopt(self.get_full_doc(), version=__version__, options_first=True, argv=argv)
        StateHolder.args.update(self.command_interpreter(command=StateHolder.args['<command>'],
                                                         argv=[] + StateHolder.args['<args>']))
        ColorPrint.set_log_level(StateHolder.args)
        ColorPrint.print_info('arguments:\n' + str(StateHolder.args), 1)

    def get_full_doc(self):
        doc = __doc__
        commands = []
        for sub_cmd in self.command_classes.keys():
            if sub_cmd is None:
                [Pocok.build_command(commands=commands, cls=cls) for cls in self.command_classes[None]]
                continue
            sub = "  " + sub_cmd + " [<subcommand>]"
            doc += sub + (42-len(sub)) * " " + "See 'pocok help " + sub_cmd + "' for more."
        doc += "\n" + "".join(commands) + "\n" + END_STRING
        return doc

    def command_interpreter(self, command, argv):
        if command == 'help':
            argv.append('-h')
            if len(argv) == 1:
                docopt(self.get_full_doc() + "\n" + CTAUtils.get_cta(), argv=argv)
            self.command_interpreter(argv[0], argv[1:])
        if command in self.command_classes.keys():
            if len(argv) == 0:
                argv.append("ls")  # TODO move to alternative handling if need
            args = self.get_args(command=command, classes=self.command_classes[command], argv=argv)
            if args is None:
                docopt(self.build_sub_commands_help(command, classes=self.command_classes[command]),
                       argv=[command] + argv)
        else:
            args = self.get_args(command=None, classes=self.command_classes[None], argv=[command] + argv)
            if args is None:
                ColorPrint.exit_after_print_messages("%r is not a pocok command. See 'pocok help'." % command)
        return args

    @staticmethod
    def build_command(commands, cls):
        sub_command = getattr(cls, 'sub_command')
        command = getattr(cls, 'command')
        description = getattr(cls, 'description')

        if command is None:
            ColorPrint.print_info("Command class not contains command: " + cls, lvl=1)
            return
        if isinstance(command, list):
            cmd = "(" + "|".join(command) + ")"
        else:
            cmd = command
        if sub_command is not None:
            cmd = "pocok " + sub_command + " " + cmd
        cmd += (40 - len(cmd)) * " "
        commands.append("  " + cmd + description + "\n")

    def get_args(self, command, classes, argv):
        for cls in classes:
            cmd = getattr(cls, 'command')
            if not isinstance(cmd, list):
                cmd = [cmd]
            if argv[0] in cmd:
                self.active_object = cls()
                return docopt(Pocok.build_command_help(cls), argv=[command] + argv if command is not None else argv)

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
        doc = "Usage:\n  pocok " + cmd
        if args is not None:
            doc += " " + " ".join(args)
        doc += "\n\n  -h, --help"
        if args is not None:
            descriptions = getattr(cls, 'args_descriptions')
            doc += "\n\n  Specific parameters:\n"
            for arg in args:
                des = descriptions[arg] if arg in descriptions else " "
                doc += "    " + arg + (40 - len(arg)) * " " + des + "\n"
        doc += "\n  " + desc
        return doc

    @staticmethod
    def build_sub_commands_help(sub_command, classes):
        doc = "Pocok " + sub_command + " commands\n\nUsage:\n"
        commands = []
        [Pocok.build_command(commands=commands, cls=cls) for cls in classes]
        return doc + "".join(commands)

    @staticmethod
    def handle_alternatives(args):
        if 'project' in args and ('ls' in args or len(args) == 1):
            return ['catalog']
        return args

    def collect_commands(self):
        try:
            command_packages = importlib.import_module('pocok.commands', package='pocok')
            for importer, modname, ispkg in pkgutil.iter_modules(command_packages.__path__):
                if not ispkg:
                    mod = importlib.import_module('pocok.commands.' + modname, 'pocok')
                    for name, cls in inspect.getmembers(mod,
                                                        lambda member: inspect.isclass(member)
                                                        and member.__module__ == mod.__name__):
                        self.check_base_class(cls)
        except ImportError as ex:
            ColorPrint.exit_after_print_messages("Commands import error: " + str(ex.args))

    def check_base_class(self, cls):
        for base_class in cls.__bases__:
            if base_class == AbstractCommand:
                sub_command = getattr(cls, 'sub_command')
                if sub_command not in self.command_classes.keys():
                    self.command_classes[sub_command] = list()
                self.command_classes[sub_command].append(cls)
                break


def main():
    pocok = Pocok()
    #try:
    pocok.start_flow()
    #except Exception as ex:
    #    ColorPrint.exit_after_print_messages(message="Unexpected error: " + type(ex).__name__ + "\n" + str(ex.args))

if __name__ == '__main__':
    sys.exit(main())

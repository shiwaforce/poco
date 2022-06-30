#!/usr/bin/env python
"""POCO - project compose.

Usage:
  poco [options] <command> [<args>...]


Options:
  -v --version         Print version of POCO
  -h --help         Show this screen.
  -V --verbose      Print more text.
  -q --quiet        Print less text.
  --always-update   Project repository handle by user
  --offline         Offline mode

The available poco commands are:
"""
import os
import sys
import traceback

from docopt import docopt

from poco.services.state_utils import StateUtils
from .commands.abstract_command import CommandState
from .services.command_holder import CommandHolder
from .services.console_logger import ColorPrint
from .services.cta_utils import CTAUtils
from .services.environment_utils import EnvironmentUtils
from .services.state import StateHolder

END_STRING = """See 'poco help <command>' for more information on a specific command."""
__version__ = '0.99.1'


class Poco(object):
    command_classes = dict()
    active_object = None

    def __init__(self, home_dir=os.path.join(os.path.expanduser(path='~'), '.poco'),
                 argv=sys.argv[1:]):

        # Set home directory to .poco in OS user home directory (~/.poco)
        StateHolder.home_dir = home_dir

        # Read common configuration from .poco file (~/.poco/.poco)
        StateUtils.prepare_config()

        # If not offline, check new version
        if not StateHolder.offline:
            EnvironmentUtils.check_version(__version__, StateHolder.is_beta_tester)

        # Set OS user id to POCO_UID and POCO_GUI environment variables
        EnvironmentUtils.set_poco_uid_and_gid()

        self.argv = argv
        CommandHolder()

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
        StateHolder.args = docopt(CommandHolder.get_full_doc(__doc__), version=__version__, options_first=True,
                                  argv=self.argv)
        StateHolder.args.update(self.command_interpreter(command=StateHolder.args['<command>'],
                                                         argv=[] + StateHolder.args['<args>']))
        ColorPrint.set_log_level(StateHolder.args)
        ColorPrint.print_info('arguments:\n' + str(StateHolder.args), 1)

    def command_interpreter(self, command, argv):
        if command == 'help':
            argv.append('-h')
            if len(argv) == 1:
                docopt(CommandHolder.get_full_doc(__doc__) + "\n" + CTAUtils.get_cta(), argv=argv)
            self.command_interpreter(argv[0], argv[1:])
        if command in CommandHolder.command_classes.keys():
            if len(argv) == 0:
                argv.append("-h")
            args = self.get_args(command=command, classes=CommandHolder.command_classes[command], argv=argv)
            if args is None:
                docopt(CommandHolder.build_sub_commands_help(command, classes=CommandHolder.command_classes[command]),
                       argv=[command] + argv)
        else:
            args = self.get_args(command=None, classes=CommandHolder.command_classes[None], argv=[command] + argv)
            if args is None:
                argv.append('-h')
                docopt(CommandHolder.get_full_doc(__doc__) + "\n\n" + "%r is not a poco command." % command, argv=argv)
        return args

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


def main():
    poco = Poco()
    try:
        poco.start_flow()
    except Exception as ex:
        if ColorPrint.log_lvl > 0:
            ColorPrint.print_error("Unexpected error: " + type(ex).__name__ + "\n" + str(ex))
            traceback.print_exc()
            sys.exit(1)
        else:
            ColorPrint.exit_after_print_messages(message="Unexpected error: " + type(ex).__name__ + "\n" + str(ex.args)
                                                         + "\nRun with '-V' for more information.")


if __name__ == '__main__':
    sys.exit(main())

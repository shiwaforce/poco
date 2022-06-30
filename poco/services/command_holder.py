import importlib
import inspect
import pkgutil

from .console_logger import ColorPrint
from ..commands.abstract_command import AbstractCommand


class CommandHolder:
    command_classes = dict()

    END_STRING = """See 'poco help <command>' for more information on a specific command."""

    def __init__(self):
        try:
            command_packages = importlib.import_module('poco.commands', package='poco')
            for importer, modname, is_package in pkgutil.iter_modules(command_packages.__path__):
                if not is_package:
                    mod = importlib.import_module('poco.commands.' + modname, 'poco')
                    mod_members = inspect.getmembers(mod, lambda member: inspect.isclass(
                        member) and member.__module__ == mod.__name__)
                    for name, class_name in mod_members:
                        self.check_base_class(class_name)
        except ImportError as ex:
            ColorPrint.exit_after_print_messages("Commands import error: " + str(ex.args))

    def check_base_class(self, class_name):
        for base_class in inspect.getmro(class_name)[1:]:
            if base_class == AbstractCommand:
                sub_command = getattr(class_name, 'sub_command')
                if sub_command not in self.command_classes.keys():
                    self.command_classes[sub_command] = list()
                self.command_classes[sub_command].append(class_name)
                break

    @staticmethod
    def get_full_doc(prefix):
        doc = prefix
        commands = []
        for sub_cmd in CommandHolder.command_classes.keys():
            if sub_cmd is None:
                [CommandHolder.build_command(commands=commands, cls=cls) for cls in CommandHolder.command_classes[None]]
                continue
            sub = "  " + sub_cmd + " [<subcommand>]"
            doc += sub + (42 - len(sub)) * " " + "See 'poco help " + sub_cmd + "' for more.\n"
        doc += "".join(commands) + "\n" + CommandHolder.END_STRING
        return doc

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

    @staticmethod
    def build_sub_commands_help(sub_command, classes):
        doc = "Poco " + sub_command + " commands\n\nUsage:\n"
        commands = []
        [CommandHolder.build_command(commands=commands, cls=cls) for cls in classes]
        return doc + "".join(commands)


def check_base_class(class_name):
    for base_class in inspect.getmro(class_name)[1:]:
        if base_class == AbstractCommand:
            sub_command = getattr(class_name, 'sub_command')
            if sub_command not in CommandHolder.command_classes.keys():
                CommandHolder.command_classes[sub_command] = list()
            CommandHolder.command_classes[sub_command].append(class_name)
            break

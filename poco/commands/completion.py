""" POCO - completion

Forrás: https://blog.deepjyoti30.dev/tab-autocomplet-cli-apps

Koncepció:
  - a bash és zsh kiegészítéshez ne keljen függőség az OS-en. Nem biztos, hogy azonos Mac-en vagy Linuxon.
  - a completion command az argumentumok alapján adjon választ. Így a Poco képes lesz a planek listázására is

Extra info:
  - https://github.com/CumulusNetworks/NetworkDocopt/blob/master/bin/network-docopt-example

"""
import os

from .abstract_command import AbstractCommand
from ..services.command_holder import CommandHolder
from ..services.state import StateHolder
from ..services.state_utils import StateUtils


class Completion(AbstractCommand):
    command = "completion"

    args = ["[<comp_line>]"]
    args_descriptions = {"[<comp_line>]": "command line competition"}
    description = "Run: 'poco completion' to get all poco command or " \
                  "'poco completion plan' to get plan commands."

    def prepare_states(self):
        StateUtils.calculate_name_and_work_dir()
        StateUtils.prepare("compose_handler")

    def resolve_dependencies(self):
        if StateHolder.catalog_element is not None and not StateUtils.check_variable('repository'):
            # Repository not found
            exit(1)
        self.check_poco_file()

    def completion(self):
        pass

    @staticmethod
    def print_first_level():
        for sub_cmd in CommandHolder.command_classes.keys():
            if sub_cmd is None:
                for cls in CommandHolder.command_classes[None]:
                    cmd = getattr(cls, 'command')
                    if isinstance(cmd, list):
                        print(*cmd, sep="\n")
                    else:
                        print(cmd)
                continue
            print(sub_cmd)

    def execute(self):
        comp_line = StateHolder.args.get('<comp_line>')
        if comp_line is None:
            self.print_first_level()
        else:
            count_of_words = len(comp_line.split())
            if count_of_words <= 1:
                self.print_first_level()
            else:
                print(f'COMPLETION ---- comp_line: [{comp_line}]')
                cls = self.resolve_command(comp_line.split())
                cls.completion()

    def resolve_command(self, words: list) -> AbstractCommand:
        argv = words
        argv.pop(0)
        return self.get_command_class(str(argv[0]), argv)

    def get_command_class(self, command: str, argv: list) -> AbstractCommand:
        if command in CommandHolder.command_classes.keys():
            return self.get_args(CommandHolder.command_classes[command], argv)
        else:
            return self.get_args(CommandHolder.command_classes[None], [command] + argv)

    @staticmethod
    def get_args(classes: list, argv: list) -> AbstractCommand:
        for cls in classes:
            cmd = getattr(cls, 'command')
            if not isinstance(cmd, list):
                cmd = [cmd]
            if argv[0] in cmd:
                return cls()

    @staticmethod
    def check_poco_file():
        if not StateUtils.check_variable('poco_file'):
            poco_file = str(StateHolder.repository.target_dir if StateHolder.repository is not None
                            else os.getcwd()) + '/poco.yml'
            exit(1)

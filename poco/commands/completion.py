""" POCO - completion

Forrás: https://blog.deepjyoti30.dev/tab-autocomplet-cli-apps

Koncepció:
  - a bash és zsh kiegészítéshez ne keljen függőség az OS-en. Nem biztos, hogy azonos Mac-en vagy Linuxon.
  - a completion command az argumentumok alapján adjon választ. Így a Poco képes lesz a planek listázására is

Extra info:
  - https://github.com/CumulusNetworks/NetworkDocopt/blob/master/bin/network-docopt-example

"""

from .abstract_command import AbstractCommand
from ..services.command_holder import CommandHolder
from ..services.state import StateHolder


class Completion(AbstractCommand):
    command = "completion"
    args = ["[<comp_line>]"]
    args_descriptions = {"[<comp_line>]": "command line competition"}
    description = "Run: 'poco completion' to get all poco command or " \
                  "'poco completion plan' to get plan commands."

    def prepare_states(self):
        pass

    def resolve_dependencies(self):
        pass

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
                self.resolve_command(comp_line.split())

    @staticmethod
    def resolve_command(words):
        print(f'command: {words[1]}')
        ch = CommandHolder.command_classes
        cmd = ch.get(words[1])
        print(f'cmdclass: {cmd}')

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

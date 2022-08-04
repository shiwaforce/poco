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
    args = ["[<prev_word>]", "[<curr_word>]"]
    args_descriptions = {"[<prev_word>]": "Previous word in the command line competition",
                         "[<curr_word>]": "Current word in the command line competition"}
    description = "Run: 'poco completion' to get all poco command or " \
                  "'poco completion plan' to get plan commands."

    def prepare_states(self):
        pass

    def resolve_dependencies(self):
        pass

    def execute(self):
        prev_word = StateHolder.args.get('<prev_word>')
        curr_word = StateHolder.args.get('<curr_word>')
        print(f'COMPLETION ---- prev_word: [{prev_word}], curr_word: [{curr_word}]')

        self.print_first_level()

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

#!/usr/bin/env python
"""SF Program service.

Usage:
  project-service [options] start [<project>]
  project-service [options] stop [<project>]
  project-service [options] restart [<project>]

  project-service (-h | --help)
  project-service --version

Options:
  -h --help     Show this screen.
  -v --verbose  Print more text.
  -q --quiet    Print less text.
  --offline     Offline mode

"""
import os
import sys
from .abstract_command import AbstractCommand
from .services.file_utils import FileUtils
from .services.console_logger import ColorPrint


class ProjectService(AbstractCommand):

    def __init__(self, home_dir=os.path.join(os.path.expanduser(path='~'), '.project-compose'), skip_docker=False,
                 argv=sys.argv[1:]):
        super(ProjectService, self).__init__(home_dir=home_dir, skip_docker=skip_docker, doc=__doc__, argv=argv)

    def run(self):

        try:
            '''Parse catalog'''
            self.parse_catalog()

            if self.arguments.get('<project>') is None:
                self.arguments['<project>'] = FileUtils.get_directory_name()

            '''Get project name'''
            self.name = self.arguments.get('<project>')
            '''Init project utils'''
            self.init_project_utils(offline=self.arguments.get("--offline"))
            '''Init compose handler'''
            self.init_compose_handler(arguments=self.arguments)

            '''Handling top level commands'''
            if self.arguments.get('start'):
                self.run_before(offline=self.arguments.get("--offline"))
                self.run_docker_command(commands="start")
                self.run_after()
            if self.arguments.get('stop'):
                self.run_before(offline=self.arguments.get("--offline"))
                self.run_docker_command(commands="stop")
                self.run_after()
            if self.arguments.get('restart'):
                self.run_before(offline=self.arguments.get("--offline"))
                self.run_docker_command(commands="restart")
                self.run_after()
        except Exception as ex:
            ColorPrint.exit_after_print_messages(message="Unexpected error:\n" + ex.message)


def main():
    service = ProjectService()
    service.run()

if __name__ == '__main__':
    sys.exit(main())

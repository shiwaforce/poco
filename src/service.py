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
from docopt import docopt


class ProjectService(AbstractCommand):

    def __init__(self, home_dir=os.path.join(os.path.expanduser(path='~'), '.project-compose')):
        super(ProjectService, self).__init__(home_dir=home_dir)

    def run(self, argv):
        arguments = docopt(__doc__, version="0.7.2", argv=argv)
        ColorPrint.set_log_level(arguments)

        #try:
        '''Parse config and catalog'''
        self.parse_config()
        self.parse_catalog()

        if arguments.get('<project>') is None:
            arguments['<project>'] = FileUtils.get_directory_name()

        '''Get project name'''
        self.name = arguments.get('<project>')
        '''Init project utils'''
        self.init_project_utils(offline=arguments.get("--offline"))
        '''Init compose handler'''
        self.init_compose_handler(arguments=arguments)

        '''Handling top level commands'''
        if arguments.get('start'):
            self.run_before(offline=arguments.get("--offline"))
            self.run_docker_command(commands="start")
            self.run_after()
        if arguments.get('stop'):
            self.run_before(offline=arguments.get("--offline"))
            self.run_docker_command(commands="stop")
            self.run_after()
        if arguments.get('restart'):
            self.run_before(offline=arguments.get("--offline"))
            self.run_docker_command(commands="restart")
            self.run_after()
        # except Exception as ex:
        #    ColorPrint.exit_after_print_messages(message="Unexpected error:\n" + ex.message)


def main():
    service = ProjectService()
    service.run(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(main())



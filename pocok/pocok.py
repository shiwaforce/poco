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
   catalog                  List the available projects in repos.
   repo [<subcommand>]      Repository commands, see 'pocok help repo' for more.
   project [<subcommand>]   Project commands, see 'pocok help project' for more.
   up, start                Start project
   down, stop               Stop project
   restart                  Restart project
   plan ls                  Print all plan belongs to project
   config                   Print full Docker compose configuration for a project's plan.
   clean                    Clean all container and image from local Docker repository.
   init                     Create pocok.yml and docker-compose.yml in project if aren't exists.
   install                  Get projects from remote repository (if its not exists locally yet) and run install scripts.
   build                    Build containers depends defined project and plan.
   ps                       Print containers statuses which depends defined project and plan.
   plan ls                  Print all available plan for the project.
   pull                     Pull all necessary image for project and plan.
   log, logs                Print containers logs which depends defined project and plan.
   branch                   Switch branch on defined project.
   branches                 List all available git branch for the project.
   pack                     Pack the selected project's plan configuration with docker images to an archive.
   unpack                   Unpack archive, install images to local repository.

See 'pocok help <command>' for more information on a specific command.

"""
import os
import shutil
import sys
from docopt import docopt
from .pocok_default import PocokDefault
from .pocok_repo import PocokRepo
from .pocok_project import PocokProject
from .services.config_handler import ConfigHandler
from .services.clean_handler import CleanHandler
from .services.compose_handler import ComposeHandler
from .services.cta_utils import CTAUtils
from .services.environment_utils import EnvironmentUtils
from .services.git_repository import GitRepository
from .services.project_utils import ProjectUtils
from .services.console_logger import ColorPrint
from .services.command_handler import CommandHandler
from .services.package_handler import PackageHandler
from .services.state import StateHolder
from .services.state_utils import StateUtils


__version__ = '0.24.0'


class Pocok(object):

    catalog_handler = None
    project_utils = None
    command_handler = None

    commands = {
        'repo': PocokRepo,
        'project': PocokProject
    }

    def __init__(self, home_dir=os.path.join(os.path.expanduser(path='~'), '.pocok'),
                 argv=sys.argv[1:]):

        EnvironmentUtils.check_version(__version__)

        StateHolder.home_dir = home_dir
        argv = Pocok.handle_alternatives(argv)
        if len(argv) == 0:
            argv.append('-h')
        StateHolder.args = docopt(__doc__, version=__version__, options_first=True, argv=argv)
        StateUtils.fill_pre_states()
        StateHolder.args.update(self.command_interpreter(command=StateHolder.args['<command>'],
                                                         argv=[] + StateHolder.args['<args>']))
        ColorPrint.set_log_level(StateHolder.args)
        ColorPrint.print_info('arguments:\n' + str(StateHolder.args), 1)
        StateUtils.fill_states()

    def command_interpreter(self, command, argv):
        args = dict()
        if command == 'help':
            argv.append('-h')
            if len(argv) == 1:
                docopt(__doc__ + self.add_cta(), options_first=True, argv=argv)
            self.command_interpreter(argv[0], argv[1:])
        if command in self.commands.keys():
            if len(argv) == 0:
                argv.append("ls")
            command_obj = self.commands[command]
            args = docopt(command_obj.command_dict.get(argv[0], command_obj.DEFAULT), argv=[command] + argv)
        elif command in PocokDefault.command_dict.keys():
            args = docopt(PocokDefault.command_dict[command], argv=[command] + argv)
        else:
            ColorPrint.exit_after_print_messages("%r is not a pocok command. See 'pocok help'." % command)
        return args

    @staticmethod
    def handle_alternatives(args):
        if 'project' in args and ('ls' in args or len(args) == 1):
            return ['catalog']

        return args

    @staticmethod
    def run():
        #try:
        ColorPrint.print_info(StateHolder.config_handler.print_config(), 1)
        if StateHolder.has_args('repo'):
            PocokRepo.handle()
        elif StateHolder.has_args('project'):
            PocokProject.handle()
        else:
            PocokDefault.handle()
        #except Exception as ex:
        #    ColorPrint.exit_after_print_messages(message="Unexpected error: " + type(ex).__name__ + "\n" + str(ex.args))

    def run_default(self):
        """Handling top level commands"""
        if StateHolder.has_args('clean'):
            CleanHandler().clean()
            ColorPrint.exit_after_print_messages(message="Clean complete", msg_type="info")
            return

        """Init project utils"""
        self.project_utils = ProjectUtils()

        if StateHolder.has_args('init'):
            self.init()
            CommandHandler(project_utils=self.project_utils).run_script("init_script")
            return

        if StateHolder.has_args('branches'):
            self.get_project_repository().print_branches()
            return

        if StateHolder.has_args('branch'):
            branch = StateHolder.args.get('<branch>')
            repo = self.get_project_repository()
            repo.set_branch(branch=branch, force=StateHolder.args.get("-f"))
            project_descriptor = self.catalog_handler.get()
            project_descriptor['branch'] = branch
            self.catalog_handler.set(modified=project_descriptor)
            ColorPrint.print_info(message="Branch changed")
            return

        if StateHolder.has_args('install'):
            self.get_project_repository()
            ColorPrint.print_info("Project installed")
            return

        if StateHolder.has_args('plan', 'ls'):
            self.init_compose_handler()
            StateHolder.compose_handler.get_plan_list()
            return

        if StateHolder.has_args('unpack'):
            PackageHandler().unpack()
            return

        self.init_compose_handler()
        self.command_handler = CommandHandler(project_utils=self.project_utils)

        if StateHolder.has_args('config'):
            self.command_handler.run('config')

        if StateHolder.has_args('build'):
            self.run_checkouts()
            self.command_handler.run('build')
            ColorPrint.print_info("Project built")

        if StateHolder.has_least_one_arg('up', 'start'):
            self.run_checkouts()
            self.command_handler.run('up')

        if StateHolder.has_args('restart'):
            self.run_checkouts()
            self.command_handler.run('restart')

        if StateHolder.has_args('down'):
            self.command_handler.run('down')
            ColorPrint.print_info("Project stopped")

        if StateHolder.has_args('ps'):
            self.run_checkouts()
            self.command_handler.run('ps')

        if StateHolder.has_args('pull'):
            self.run_checkouts()
            self.command_handler.run('pull')
            ColorPrint.print_info("Project pull complete")

        if StateHolder.has_args('stop'):
            self.command_handler.run('stop')

        if StateHolder.has_least_one_arg('logs', 'log'):
            self.command_handler.run('logs')
            return

        if StateHolder.has_args('pack'):
            self.command_handler.run('pack')

    def init(self):
        project_element = self.get_catalog()
        repo = self.get_project_repository()

        file = repo.get_file(project_element.get('file')) if project_element is not None else None
        # TODO
        if file is None:
            if os.path.exists('pocok.yaml'):
                file = 'pocok.yaml'
            else:
                file = 'pocok.yml'

        if not os.path.exists(file):
            src_file = os.path.join(os.path.dirname(__file__), 'services/resources/pocok.yml')
            shutil.copyfile(src=src_file, dst=file)
            default_compose = os.path.join(os.path.dirname(file), 'docker-compose.yml')
            if not os.path.exists(default_compose):
                src_file = os.path.join(os.path.dirname(__file__), 'services/resources/docker-compose.yml')
                shutil.copyfile(src=src_file, dst=default_compose)
        self.init_compose_handler()
        ColorPrint.print_info("Project init completed")

    def get_catalog(self):
        if self.catalog_handler is not None:
            return self.catalog_handler.get()

    def get_compose_file(self, silent=False):
        catalog = self.get_catalog()
        return self.project_utils.get_compose_file(project_element=catalog,
                                                   ssh=self.get_node(catalog, ["ssh-key"]), silent=silent)

    def get_project_repository(self):
        catalog = self.get_catalog()
        if catalog is None:
            return self.project_utils.add_repository(target_dir=StateHolder.work_dir)
        return self.project_utils.get_project_repository(project_element=catalog,
                                                         ssh=self.get_node(catalog, ["ssh-key"]))

    def get_repository_dir(self):
        if StateHolder.config is None:
            return os.getcwd()
        return self.project_utils.get_target_dir(self.catalog_handler.get())

    def add_cta(self):
        res = ""
        if self.one_of_local_files_exits(files=['pocok.yml', 'pocok.yaml']):
            res = CTAUtils.CTA_STRINGS['have_all']
        elif not ConfigHandler.exists() and \
                self.one_of_local_files_exits(files=['docker-compose.yml', 'docker-compose.yaml', '.poco', 'docker']) \
                and not self.one_of_local_files_exits(files=['pocok.yml', 'pocok.yaml']):
            res = CTAUtils.CTA_STRINGS['have_file']
        elif not ConfigHandler.exists() and not \
                self.one_of_local_files_exits(files=['docker-compose.yml', 'docker-compose.yaml', '.poco', 'docker']):
            res = CTAUtils.CTA_STRINGS['default']
        elif ConfigHandler.exists():
            res = CTAUtils.CTA_STRINGS['have_cat']
        return res

    @staticmethod
    def one_of_local_files_exits(files):
        actual_dir = os.getcwd()
        ''' TODO handle extension'''
        for file in files:
            if os.path.exists(os.path.join(actual_dir, file)):
                return True
        return False

    @staticmethod
    def run_checkouts():
        for checkout in StateHolder.compose_handler.get_checkouts():
            if " " not in checkout:
                ColorPrint.exit_after_print_messages(message="Wrong checkout command: " + checkout)
            directory, repository = checkout.split(" ")
            target_dir = os.path.join(StateHolder.compose_handler.get_working_directory(), directory)
            if not StateHolder.offline:
                GitRepository(target_dir=target_dir, url=repository, branch="master")
            if not os.path.exists(target_dir):
                ColorPrint.exit_after_print_messages("checkout directory is empty: " + str(directory))

    def init_compose_handler(self):
        StateHolder.compose_handler = ComposeHandler(compose_file=self.get_compose_file(),
                                                     plan=StateHolder.args.get('<plan>'),
                                                     repo_dir=self.get_repository_dir())

    @staticmethod
    def get_node(structure, paths, default=None):
        if structure is None:
            return None
        node = paths[0]
        paths = paths[1:]

        while node in structure and len(paths) > 0:
            structure = structure[node]
            node = paths[0]
            paths = paths[1:]

        return structure[node] if node in structure else default


def main():
    pocok = Pocok()
    pocok.run()

if __name__ == '__main__':
    sys.exit(main())

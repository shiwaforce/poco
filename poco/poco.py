#!/usr/bin/env python
"""SF Program compose.

Usage:
  poco catalog [options] add [<target-dir>] [<catalog>]
  poco catalog [options] ls
  poco catalog [options] config
  poco catalog [options] branch <branch> [<catalog>] [-f]
  poco catalog [options] branches [<catalog>]
  poco catalog [options] push [<catalog>]
  poco catalog [options] remove [<project>]
  poco [options] config [<project>] [<plan>]
  poco [options] clean
  poco [options] init [<project>]
  poco [options] install [<project>] [<plan>]
  poco [options] up [<project>] [<plan>]
  poco [options] down [<project>] [<plan>]
  poco [options] build [<project>] [<plan>]
  poco [options] ps [<project>] [<plan>]
  poco [options] plan ls [<project>]
  poco [options] pull [<project>] [<plan>]
  poco [options] restart [<project>] [<plan>]
  poco [options] start [<project>] [<plan>]
  poco [options] stop [<project>] [<plan>]
  poco [options] log [<project>] [<plan>]
  poco [options] logs [<project>] [<plan>]
  poco [options] branch <project> <branch> [-f]
  poco [options] branches [<project>]

  poco (-h | --help)
  poco --version

Options:
  -h --help     Show this screen.
  -v --verbose  Print more text.
  -q --quiet    Print less text.
  --developer   Project repository handle by user
  --offline     Offline mode

"""
import os
import shutil
import sys
from docopt import docopt
from subprocess import Popen, PIPE
from .services.catalog_handler import CatalogHandler
from .services.clean_handler import CleanHandler
from .services.compose_handler import ComposeHandler
from .services.config_handler import ConfigHandler
from .services.file_utils import FileUtils
from .services.git_repository import GitRepository
from .services.project_utils import ProjectUtils
from .services.console_logger import ColorPrint
from .services.command_handler import CommandHandler
from .services.state import StateHolder


__version__ = '0.18.0'


class Poco(object):

    config_handler = None
    catalog_handler = None
    project_utils = None
    compose_handler = None
    command_handler = None
    state = StateHolder

    def __init__(self, home_dir=os.path.join(os.path.expanduser(path='~'), '.poco'),
                 argv=sys.argv[1:]):

        """Fill state"""

        self.state.home_dir = home_dir
        self.state.log_dir = os.path.join(StateHolder.home_dir, 'logs')
        self.state.config_file = os.path.join(StateHolder.home_dir, 'config')
        if not self.state.skip_docker:
            self.check_docker()
        self.arguments = docopt(__doc__, version=__version__, argv=argv)
        ColorPrint.set_log_level(self.arguments)

        if self.arguments.get('<project>') is None:
            self.arguments['<project>'] = FileUtils.get_directory_name()
        self.state.name = self.arguments.get('<project>')
        self.state.offline = self.arguments.get("--offline")

        """Parse config """
        self.config_handler = ConfigHandler()
        self.config_handler.read()

        if self.arguments.get("--developer"):
            self.state.developer_mode = self.arguments.get("--developer")

    def run(self):
        try:
            if self.has_attributes('catalog', 'config'):
                self.config_handler.dump()
                return

            """Parse catalog"""
            self.catalog_handler = CatalogHandler()

            if self.has_attributes('catalog', 'ls'):
                self.print_ls()
                return
            if self.has_attributes('catalog', 'branches'):
                self.print_branches(repo=self.catalog_handler.get_catalog_repository(self.arguments.get('<catalog>')))
                return
            if self.has_attributes('catalog', 'branch'):
                branch = self.arguments.get('<branch>')
                self.set_branch(branch=branch, force=self.arguments.get("-f"))
                ColorPrint.print_info("Branch changed")
                return
            if self.has_attributes('catalog', 'push'):
                self.catalog_handler.push(self.arguments.get('<catalog>'))
                ColorPrint.print_info("Push completed")
                return
            if self.has_attributes('catalog', 'add'):
                target_dir = FileUtils.get_normalized_dir(self.arguments.get('<target-dir>'))
                repo, repo_dir = FileUtils.get_git_repo(target_dir)
                self.add_to_catalog(target_dir=target_dir, repo_dir=repo_dir, repo=repo,
                                    catalog=self.arguments.get('<catalog>'))
                ColorPrint.print_info("Project added")
                return

            '''Handling top level commands'''
            if self.has_attributes('clean'):
                CleanHandler().clean()
                ColorPrint.exit_after_print_messages(message="Clean complete", msg_type="info")
                return

            '''Init project utils'''
            self.project_utils = ProjectUtils()

            if self.has_attributes('catalog', 'remove'):
                ColorPrint.print_info("Project removed")
                self.remove_from_catalog(self.arguments)
                return

            if self.has_attributes('branches'):
                self.print_branches(repo=self.get_project_repository())
                return

            if self.has_attributes('branch'):
                branch = self.arguments.get('<branch>')
                repo = self.get_project_repository()
                repo.set_branch(branch=branch, force=self.arguments.get("-f"))
                project_descriptor = self.catalog_handler.get()
                project_descriptor['branch'] = branch
                self.catalog_handler.set(modified=project_descriptor)
                ColorPrint.print_info(message="Branch changed")
                return

            if self.has_attributes('install'):
                self.get_project_repository()
                ColorPrint.print_info("Project installed")
                return

            if self.has_attributes('init'):
                self.init()
                '''Init compose handler'''
                self.init_compose_handler(arguments=self.arguments)
                CommandHandler(args=self.arguments,
                               compose_handler=self.compose_handler,
                               project_utils=self.project_utils).run_script("init_script")
                return

            '''Init compose handler'''
            self.init_compose_handler(arguments=self.arguments)

            if self.has_attributes('plan', 'ls'):
                self.compose_handler.get_plan_list()
                return

            self.command_handler = CommandHandler(args=self.arguments,
                                                  compose_handler=self.compose_handler,
                                                  project_utils=self.project_utils)

            if self.has_attributes('config'):
                self.command_handler.run('config')

            if self.has_attributes('build'):
                self.run_before()
                self.command_handler.run('build')
                ColorPrint.print_info("Project built")

            if self.has_attributes('up') or self.has_attributes('start'):
                self.run_before()
                self.command_handler.run('up')

            if self.has_attributes('restart'):
                self.run_before()
                self.command_handler.run('restart')

            if self.has_attributes('down'):
                self.command_handler.run('down')
                ColorPrint.print_info("Project stopped")

            if self.has_attributes('ps'):
                self.run_before()
                self.command_handler.run('ps')

            if self.has_attributes('pull'):
                self.run_before()
                self.command_handler.run('pull')
                ColorPrint.print_info("Project pull complete")

            if self.has_attributes('stop'):
                self.command_handler.run('stop')

            if self.has_attributes('logs') or self.has_attributes('log'):
                self.command_handler.run('logs')

        except Exception as ex:
            ColorPrint.exit_after_print_messages(message="Unexpected error: " + type(ex).__name__ + "\n" + str(ex.args))

    def init(self):
        project_element = self.get_catalog()
        repo = self.get_project_repository()
        file = repo.get_file(project_element.get('file', 'poco.yml'))

        if not os.path.exists(file):
            src_file = os.path.join(os.path.dirname(__file__), 'services/resources/poco.yml')
            shutil.copyfile(src=src_file, dst=file)
            default_compose = os.path.join(os.path.dirname(file), 'docker-compose.yml')
            if not os.path.exists(default_compose):
                src_file = os.path.join(os.path.dirname(__file__), 'services/resources/docker-compose.yml')
                shutil.copyfile(src=src_file, dst=default_compose)
        ColorPrint.print_info("Project init completed")

    def has_attributes(self, *args):
        for arg in args:
            if not self.arguments.get(arg):
                return False
        return True

    def get_catalog(self):
        return self.catalog_handler.get()

    def get_compose_file(self, silent=False):
        catalog = self.get_catalog()
        return self.project_utils.get_compose_file(project_element=catalog,
                                                   ssh=self.get_node(catalog, ["ssh-key"]), silent=silent)

    def get_project_repository(self):
        catalog = self.get_catalog()
        return self.project_utils.get_project_repository(project_element=catalog,
                                                         ssh=self.get_node(catalog, ["ssh-key"]))

    def init_compose_handler(self, arguments):
        compose_file = self.get_compose_file()
        repo_dir = self.project_utils.get_target_dir(self.catalog_handler.get())
        self.compose_handler = ComposeHandler(compose_file=compose_file,
                                              plan=arguments.get('<plan>'),
                                              repo_dir=repo_dir)

    def run_before(self):
        self.save_docker_config()
        self.run_checkouts()

    def run_checkouts(self):
        for checkout in self.compose_handler.get_checkouts():
            if " " not in checkout:
                ColorPrint.exit_after_print_messages(message="Wrong checkout command: " + checkout)
            directory, repository = checkout.split(" ")
            target_dir = os.path.join(self.compose_handler.get_working_directory(), directory)
            if not self.state.offline:
                GitRepository(target_dir=target_dir, url=repository, branch="master")
            if not os.path.exists(target_dir):
                ColorPrint.exit_after_print_messages("checkout directory is empty: " + str(directory))

    def save_docker_config(self):
        p = Popen(" ".join(self.compose_handler.get_command(commands="config",
                  get_file=self.project_utils.get_file)),
                  cwd=self.compose_handler.get_working_directory(),
                  env=self.compose_handler.get_environment_variables(get_file=self.project_utils.get_file),
                  stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        FileUtils.write_compose_log(directory=self.state.log_dir, data=err if len(err) > 0 else out)

    def add_to_catalog(self, target_dir, repo_dir, repo, catalog=None):
        file_prefix = ""
        repo_name = None
        if target_dir != repo_dir:
            file_prefix = FileUtils.get_relative_path(base_path=repo_dir, target_path=target_dir)
            repo_name = os.path.basename(repo_dir)
        self.catalog_handler.add_to_list(name=os.path.basename(target_dir), handler="git", catalog=catalog,
                                         url=repo.remotes.origin.url, file=file_prefix + "poco.yml",
                                         repo_name=repo_name)

    def remove_from_catalog(self, arguments):
        self.state.name = arguments.get('<project>')
        if self.state.name in self.catalog_handler.get_catalog():
            if self.get_compose_file(silent=True) is not None:
                CommandHandler(args=self.arguments,
                               compose_handler=self.compose_handler,
                               project_utils=self.project_utils).run_script("remove_script")
        self.catalog_handler.remove_from_list()

    def set_branch(self, branch, force=False):
        catalog = self.arguments.get('<catalog>')
        self.catalog_handler.get_catalog_repository(
            catalog=catalog).set_branch(branch=branch, force=force)
        self.config_handler.set_branch(branch=branch, config=catalog)

    @staticmethod
    def get_node(structure, paths, default=None):
        node = paths[0]
        paths = paths[1:]

        while node in structure and len(paths) > 0:
            structure = structure[node]
            node = paths[0]
            paths = paths[1:]

        return structure[node] if node in structure else default

    def print_ls(self):
        """Get catalog list"""
        lst = self.catalog_handler.get_catalog()
        if len(lst) > 0:
            ColorPrint.print_with_lvl(message="-------------------", lvl=-1)
            ColorPrint.print_with_lvl(message="Available projects:", lvl=-1)
            ColorPrint.print_with_lvl(message="-------------------", lvl=-1)

            for cat in lst.keys():
                for key in lst[cat].keys():
                    msg = key
                    if os.path.exists(os.path.join(
                            StateHolder.work_dir,
                            lst[cat][key]["repository_dir"] if "repository_dir" in lst[cat][key] else key)):
                        msg += " (*)"
                    ColorPrint.print_with_lvl(message=msg, lvl=-1)
        else:
            ColorPrint.print_with_lvl(
                message="Project catalog is empty. You can add projects with 'project-catalog add' command",
                lvl=-1)

    @staticmethod
    def check_docker():
        p = Popen("docker version -f {{.Server.Version}}",
                  stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        if not len(err) == 0 or len(out) == 0:
            ColorPrint.exit_after_print_messages(message='Docker not running.')
        if str(out).split(".")[0] < str(17):
            ColorPrint.exit_after_print_messages(message='Please upgrade Docker to version 17 or above')

    @staticmethod
    def print_branches(repo):
        """Get available branches"""
        actual_branch = repo.get_actual_branch()
        ColorPrint.print_with_lvl(message="----------------------------------------------------------", lvl=-1)
        ColorPrint.print_with_lvl(message="Available branches in " + repo.target_dir, lvl=-1)
        ColorPrint.print_with_lvl(message="----------------------------------------------------------", lvl=-1)
        for key in repo.get_branches():
            ColorPrint.print_with_lvl(message=str(key) + "(*)" if str(key) == actual_branch else key, lvl=-1)


def main():
    poco = Poco()
    poco.run()

if __name__ == '__main__':
    sys.exit(main())

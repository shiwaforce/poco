#!/usr/bin/env python
"""SF Program compose.

Usage:
  project-catalog [options] add [<target-dir>]
  project-catalog [options] ls
  project-catalog [options] config
  project-catalog [options] init [<repository-url>] [<repository-type>] [<file>]
  project-catalog [options] install [<project>] [<plan>]
  project-catalog [options] branch <branch> [-f]
  project-catalog [options] branches
  project-catalog [options] push
  project-catalog [options] remove [<project>]

  project-catalog -h | --help
  project-catalog --version

Options:
  -h --help     Show this screen.
  -v --verbose  Print more text.
  -q --quiet    Print less text.
  --offline     Offline mode

"""
import os
import sys
import yaml
from .abstract_command import AbstractCommand
from .services.config_handler import ConfigHandler
from .services.console_logger import ColorPrint
from .services.file_utils import FileUtils
from docopt import docopt


class ProjectCatalog(AbstractCommand):

    def __init__(self, home_dir=os.path.join(os.path.expanduser(path='~'), '.project-compose')):
        super(ProjectCatalog, self).__init__(home_dir=home_dir)
        self.check_docker()

    def run(self, argv):
        arguments = docopt(__doc__, version="0.8.0", argv=argv)
        ColorPrint.set_log_level(arguments)

        try:
            if arguments.get('init'):
                self.config_handler = ConfigHandler(home_dir=self.home_dir)
                self.config_handler.init(repo_url=arguments.get("<repository-url>"),
                                         repo_type=arguments.get("<repository-type>"),
                                         file=arguments.get("<file>"))
                ColorPrint.print_info("Init completed")

            self.parse_config()

            if arguments.get('config'):
                ColorPrint.print_info(message=yaml.dump(
                    data=self.config_handler.get_config(), default_flow_style=False, default_style='', indent=4),
                    lvl=-1)

            if not arguments.get('init') and not arguments.get('config'):
                self.parse_catalog(offline=arguments.get("--offline"))

                if arguments.get('ls'):
                    self.print_ls()
                if arguments.get('branches'):
                    self.print_branches(repo=self.catalog_handler.get_catalog_repository())
                if arguments.get('branch'):
                    branch = arguments.get('<branch>')
                    self.set_branch(branch=branch, force=arguments.get("-f"))
                    ColorPrint.print_info("Branch changed")
                if arguments.get('push'):
                    self.catalog_handler.push()
                    ColorPrint.print_info("Push completed")
                if arguments.get('add'):
                    target_dir = FileUtils.get_normalized_dir(arguments.get('<target-dir>'))
                    repo, repo_dir = FileUtils.get_git_repo(target_dir)
                    self.add_to_catalog(target_dir=target_dir, repo_dir=repo_dir, repo=repo)
                    ColorPrint.print_info("Project added")

                if arguments.get('<project>') is None:
                    arguments['<project>'] = FileUtils.get_directory_name()
                self.name = arguments.get('<project>')
                if arguments.get('remove'):
                    ColorPrint.print_info("Project removed")
                    self.remove_from_catalog(arguments)
                if arguments.get('install'):
                    '''Init project utils'''
                    self.init_project_utils(offline=arguments.get("--offline"))
                    self.get_project_repository()
                    ColorPrint.print_info("Project installed")
        except Exception as ex:
            ColorPrint.exit_after_print_messages(message="Unexpected error:\n" + ex.message)

    def print_ls(self):
        """Get catalog list"""
        lst = self.get_catalog_list()
        if len(lst) > 0:
            ColorPrint.print_with_lvl(message="-------------------", lvl=-1)
            ColorPrint.print_with_lvl(message="Available projects:", lvl=-1)
            ColorPrint.print_with_lvl(message="-------------------", lvl=-1)

            for key in lst.keys():
                msg = key
                if os.path.exists(os.path.join(self.config_handler.get_work_dir(),
                                                lst[key]["repository_dir"] if "repository_dir" in lst[key] else key)):
                    msg += " (*)"
                ColorPrint.print_with_lvl(message=msg, lvl=-1)
        else:
            ColorPrint.print_with_lvl(
                message="Project catalog is empty. You can add projects with 'project-catalog add' command",
                lvl=-1)

    def add_to_catalog(self, target_dir, repo_dir, repo):
        file_prefix = ""
        repo_name = None
        if target_dir != repo_dir:
            file_prefix = FileUtils.get_relative_path(base_path=repo_dir, target_path=target_dir)
            repo_name = os.path.basename(repo_dir)
        self.catalog_handler.add_to_list(name=os.path.basename(target_dir), handler="git",
                                         url=repo.remotes.origin.url, file=file_prefix + "project-compose.yml",
                                         repo_name=repo_name)

    def remove_from_catalog(self, arguments):
        self.name = arguments.get('<project>')
        if self.name in self.catalog_handler.get_catalog():
            '''Init project utils'''
            self.init_project_utils(offline=arguments.get("--offline"))
            if self.get_compose_file(silent=True) is not None:
                self.run_scripts(script_type="remove_script")
        self.catalog_handler.remove_from_list(name=self.name)

    def set_branch(self, branch, force=False):
        self.catalog_handler.get_catalog_repository().set_branch(branch=branch, force=force)
        self.config_handler.set_branch(branch=branch)


def main():
    catalog = ProjectCatalog()
    catalog.run(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(main())

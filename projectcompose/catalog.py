#!/usr/bin/env python
"""SF Program compose.

Usage:
  project-catalog [options] add [<target-dir>] [<catalog>]
  project-catalog [options] ls
  project-catalog [options] config
  project-catalog [options] install [<project>] [<plan>]
  project-catalog [options] branch <branch> [<catalog>] [-f]
  project-catalog [options] branches [<catalog>]
  project-catalog [options] push [<catalog>]
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
from .services.console_logger import ColorPrint
from .services.file_utils import FileUtils


class ProjectCatalog(AbstractCommand):

    def __init__(self, home_dir=os.path.join(os.path.expanduser(path='~'), '.project-compose'), skip_docker=False,
                 argv=sys.argv[1:]):
        super(ProjectCatalog, self).__init__(home_dir=home_dir, skip_docker=skip_docker, doc=__doc__, argv=argv)

    def run(self):
        try:
            if self.arguments.get('config'):
                ColorPrint.print_info(message=yaml.dump(
                    data=self.config_handler.get_config(), default_flow_style=False, default_style='', indent=4),
                    lvl=-1)

            if not self.arguments.get('init') and not self.arguments.get('config'):
                self.parse_catalog(offline=self.arguments.get("--offline"))

                if self.arguments.get('ls'):
                    self.print_ls()
                if self.arguments.get('branches'):
                    self.print_branches(repo=self.catalog_handler.get_catalog_repository(self.arguments.get('<catalog>')))
                if self.arguments.get('branch'):
                    branch = self.arguments.get('<branch>')
                    self.set_branch(branch=branch, force=self.arguments.get("-f"))
                    ColorPrint.print_info("Branch changed")
                if self.arguments.get('push'):
                    self.catalog_handler.push(self.arguments.get('<catalog>'))
                    ColorPrint.print_info("Push completed")
                if self.arguments.get('add'):
                    target_dir = FileUtils.get_normalized_dir(self.arguments.get('<target-dir>'))
                    repo, repo_dir = FileUtils.get_git_repo(target_dir)
                    self.add_to_catalog(target_dir=target_dir, repo_dir=repo_dir, repo=repo,
                                        catalog=self.arguments.get('<catalog>'))
                    ColorPrint.print_info("Project added")

                if self.arguments.get('<project>') is None:
                    self.arguments['<project>'] = FileUtils.get_directory_name()
                self.name = self.arguments.get('<project>')
                if self.arguments.get('remove'):
                    ColorPrint.print_info("Project removed")
                    self.remove_from_catalog(self.arguments)
                if self.arguments.get('install'):
                    '''Init project utils'''
                    self.init_project_utils(offline=self.arguments.get("--offline"))
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

            for cat in lst.keys():
                for key in lst[cat].keys():
                    msg = key
                    if os.path.exists(os.path.join(
                            self.config_handler.get_work_dir(),
                            lst[cat][key]["repository_dir"] if "repository_dir" in lst[cat][key] else key)):
                            msg += " (*)"
                    ColorPrint.print_with_lvl(message=msg, lvl=-1)
        else:
            ColorPrint.print_with_lvl(
                message="Project catalog is empty. You can add projects with 'project-catalog add' command",
                lvl=-1)

    def add_to_catalog(self, target_dir, repo_dir, repo, catalog=None):
        file_prefix = ""
        repo_name = None
        if target_dir != repo_dir:
            file_prefix = FileUtils.get_relative_path(base_path=repo_dir, target_path=target_dir)
            repo_name = os.path.basename(repo_dir)
        self.catalog_handler.add_to_list(name=os.path.basename(target_dir), handler="git", catalog=catalog,
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
        catalog = self.arguments.get('<catalog>')
        self.catalog_handler.get_catalog_repository(
            catalog=catalog).set_branch(branch=branch, force=force)
        self.config_handler.set_branch(branch=branch, config=catalog)


def main():
    catalog = ProjectCatalog()
    catalog.run()

if __name__ == '__main__':
    sys.exit(main())

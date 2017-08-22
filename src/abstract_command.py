import os
from docopt import docopt
from subprocess import Popen, call, check_call, PIPE
from .services.config_handler import ConfigHandler
from .services.catalog_handler import CatalogHandler
from .services.compose_handler import ComposeHandler
from .services.console_logger import ColorPrint
from .services.project_utils import ProjectUtils
from .services.git_repository import GitRepository
from .services.file_utils import FileUtils


class AbstractCommand(object):

    config_handler = None
    catalog_handler = None
    project_utils = None
    compose_handler = None

    '''project name'''
    name = None

    def __init__(self, home_dir, skip_docker, doc, argv):
        self.home_dir = home_dir
        self.skip_docker = skip_docker
        if not skip_docker:
            self.check_docker()
        self.arguments = docopt(doc, version="0.10.0", argv=argv)
        ColorPrint.set_log_level(self.arguments)
        ''' Parse config '''
        self.parse_config()

    @staticmethod
    def check_docker():
        p = Popen(["docker", "version", "-f", "'{{split (.Server.Version) \".\"}}'"],
                  stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not len(err) == 0 or len(out) == 0:
            ColorPrint.exit_after_print_messages(message='Docker not running.')
        if out[0] < 17:
            ColorPrint.exit_after_print_messages(message='Please upgrade Docker to version 17 or above')

    def parse_config(self):
        self.config_handler = ConfigHandler(home_dir=self.home_dir)

    def parse_catalog(self, offline):
        self.catalog_handler = CatalogHandler(home_dir=self.home_dir, config=self.config_handler.get_config(),
                                              offline=offline)

    def init_project_utils(self, offline):
        self.project_utils = ProjectUtils(home_dir=self.home_dir, work_dir=self.config_handler.get_work_dir(),
                                          offline=offline)

    def get_project_repository(self):
        catalog = self.get_catalog(self.name)
        return self.project_utils.get_project_repository(name=self.name, project_element=catalog,
                                                         ssh=self.get_node(catalog, ["ssh-key"]))

    def get_compose_file(self, silent=False):
        catalog = self.get_catalog(self.name)
        return self.project_utils.get_compose_file(name=self.name, project_element=catalog,
                                                   ssh=self.get_node(catalog, ["ssh-key"]), silent=silent)

    def init_compose_handler(self, arguments):
        compose_file = self.get_compose_file()
        repo_dir = self.project_utils.get_target_dir(self.config_handler.get_work_dir(), self.name,
                                                     self.catalog_handler.get(name=self.name))
        self.compose_handler = ComposeHandler(compose_file=compose_file,
                                              plan=arguments.get('<plan>'),
                                              repo_dir=repo_dir)

    def run_before(self, offline):
        self.run_scripts(script_type="before_script")
        self.run_checkouts(offline=offline)
        self.save_docker_config()

    def run_after(self):
        call(["docker", "ps"])
        self.run_scripts(script_type="after_script")

    def run_scripts(self, script_type):
        for script in self.compose_handler.get_scripts(script_type=script_type):
            check_call(script.split(' '), cwd=self.compose_handler.get_working_directory())

    def run_docker_command(self, commands):
        cmd = self.compose_handler.get_command(name=self.name, commands=commands, get_file=self.project_utils.get_file)
        ColorPrint.print_with_lvl(message="Docker command: " + str(cmd), lvl=1)
        call(cmd,
             cwd=self.compose_handler.get_working_directory(),
             env=self.compose_handler.get_environment_variables(name=self.name, get_file=self.project_utils.get_file))

    def run_checkouts(self, offline):
        for checkout in self.compose_handler.get_checkouts():
            if " " not in checkout:
                ColorPrint.exit_after_print_messages(message="Wrong checkout command: " + checkout)
            directory, repository = checkout.split(" ")
            target_dir = os.path.join(self.compose_handler.get_working_directory(), directory)
            if not offline:
                GitRepository(target_dir=target_dir, url=repository, branch="master")
            if not os.path.exists(target_dir):
                ColorPrint.exit_after_print_messages("checkout directory is empty: " + str(directory))

    def save_docker_config(self):
        p = Popen(self.compose_handler.get_command(name=self.name, commands="config",
                  get_file=self.project_utils.get_file),
                  cwd=self.compose_handler.get_working_directory(),
                  env=self.compose_handler.get_environment_variables(name=self.name,
                                                                     get_file=self.project_utils.get_file),
                  stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        FileUtils.write_compose_log(directory=self.config_handler.log_dir, project=self.name,
                                    data=err if len(err) > 0 else out)

    def get_catalog_list(self):
        return self.catalog_handler.get_catalog()

    def get_catalog(self, name):
        return self.catalog_handler.get(name=name)

    @staticmethod
    def get_node(structure, paths, default=None):
        node = paths[0]
        paths = paths[1:]

        while node in structure and len(paths) > 0:
            structure = structure[node]
            node = paths[0]
            paths = paths[1:]

        return structure[node] if node in structure else default

    @staticmethod
    def print_branches(repo):
        """Get available branches"""
        actual_branch = repo.get_actual_branch()
        ColorPrint.print_with_lvl(message="----------------------------------------------------------", lvl=-1)
        ColorPrint.print_with_lvl(message="Available branches in " + repo.target_dir, lvl=-1)
        ColorPrint.print_with_lvl(message="----------------------------------------------------------", lvl=-1)
        for key in repo.get_branches():
            ColorPrint.print_with_lvl(message=str(key) + "(*)" if str(key) == actual_branch else key, lvl=-1)

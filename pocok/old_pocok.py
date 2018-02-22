import os
import shutil
from .services.state import StateHolder
from .services.console_logger import ColorPrint
from .pocok_repo import PocokRepo
from .pocok_project import PocokProject
from .pocok_default import PocokDefault
from .services.clean_handler import CleanHandler
from .services.command_handler import CommandHandler
from .services.project_utils import ProjectUtils
from .services.package_handler import PackageHandler


COMMANDS = """
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
   pull                     Pull all necessary image for project and plan.
   log, logs                Print containers logs which depends defined project and plan.
   branch                   Switch branch on defined project.
   branches                 List all available git branch for the project.
   pack                     Pack the selected project's plan configuration with docker images to an archive.
   unpack                   Unpack archive, install images to local repository.
"""


class Pocok(object):
    catalog_handler = None
    project_utils = None
    command_handler = None

    @staticmethod
    def run():
        # try:
        ColorPrint.print_info(StateHolder.config_handler.print_config(), 1)
        if StateHolder.has_args('repo'):
            PocokRepo.handle()
        elif StateHolder.has_args('project'):
            PocokProject.handle()
        else:
            PocokDefault.handle()
            # except Exception as ex:
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

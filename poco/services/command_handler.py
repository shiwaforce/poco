import os
import yaml
import platform
from .console_logger import ColorPrint, Doc
from .file_utils import FileUtils
from .project_utils import ProjectUtils
from .environment_utils import EnvironmentUtils
from .package_handler import PackageHandler
from .state import StateHolder
from .command_runners import ScriptPlanRunner, DockerPlanRunner, KubernetesRunner, HelmRunner


class CommandHandler(object):

    def __init__(self):

        self.hierarchy = self.load_hierarchy()
        StateHolder.compose_handler.get_compose_project()
        self.project_compose = StateHolder.compose_handler.compose_project
        self.working_directory = StateHolder.compose_handler.get_working_directory()
        self.plan = StateHolder.compose_handler.plan
        self.repo_dir = StateHolder.repository.target_dir if StateHolder.repository is not None else os.getcwd()

        ''' Check mode '''
        plan = self.project_compose['plan'][self.plan]
        if isinstance(plan, dict) and ('kubernetes-file' in plan or 'kubernetes-dir' in plan):
            StateHolder.container_mode = "Kubernetes"
        elif isinstance(plan, dict) and ('helm-file' in plan or 'helm-dir' in plan):
            StateHolder.container_mode = "Helm"
        self.script_runner = ScriptPlanRunner(project_compose=self.project_compose,
                                              working_directory=self.working_directory)

        if StateHolder.container_mode == "Docker":
            EnvironmentUtils.check_docker()
        elif StateHolder.container_mode == "Kubernetes":
            EnvironmentUtils.check_kubernetes()
        elif StateHolder.container_mode == "Helm":
            EnvironmentUtils.check_helm()

    @staticmethod
    def load_hierarchy():
        with open(os.path.join(os.path.dirname(__file__), 'resources/command-hierarchy.yml')) as stream:
            try:
                return yaml.load(stream=stream)
            except yaml.YAMLError as exc:
                ColorPrint.exit_after_print_messages(message="Error: Wrong YAML format:\n " + str(exc),
                                                     doc=Doc.POCO)

    def run_script(self, script):
        self.script_runner.run(plan=self.project_compose['plan'][self.plan], script_type=script)

    def run(self, cmd):
        self.check_command(cmd)
        plan = self.project_compose['plan'][self.plan]
        command_list = self.hierarchy[cmd]

        if not isinstance(command_list, dict):
            ColorPrint.print_info("Wrong command in hierarchy: " + str(command_list))

        self.pre_run(command_list, plan)
        if isinstance(plan, dict) and 'script' in plan:
            # script running only if start or up command
            if cmd == 'start' or cmd == 'up':
                self.script_runner.run(plan=plan, script_type='script')
        elif StateHolder.container_mode in ['Kubernetes', 'Helm']:
            self.run_kubernetes(cmd, command_list, plan)
        else:
            self.run_docker(cmd, command_list, plan)
        self.after_run(command_list, plan)

    def run_docker(self, cmd, command_list, plan):
        runner = DockerPlanRunner(project_compose=self.project_compose,
                                  working_directory=self.working_directory,
                                  repo_dir=self.repo_dir)
        if StateHolder.always_update and cmd in ('start', 'up', 'restart'):  # Pull before start in developer mode
            runner.run(plan=plan, commands='pull', envs=self.get_environment_variables(plan=plan))
        for cmd in command_list['docker']:
            if cmd == 'pull' and StateHolder.offline:  # Skip pull in offline mode
                continue
            runner.run(plan=plan, commands=cmd,
                       envs=self.get_environment_variables(plan=plan))

    def run_kubernetes(self, cmd, command_list, plan):
        runner = KubernetesRunner(working_directory=self.working_directory, repo_dir=self.repo_dir) \
            if StateHolder.container_mode == 'Kubernetes' \
            else HelmRunner(working_directory=self.working_directory, repo_dir=self.repo_dir)

        if len(command_list[StateHolder.container_mode.lower()]) == 0:
            ColorPrint.exit_after_print_messages('Command: ' + cmd + ' not supported with' + StateHolder.container_mode)
        for cmd in command_list[StateHolder.container_mode.lower()]:
            runner.run(plan=plan, commands=cmd, envs=self.get_environment_variables(plan=plan))

    def check_command(self, cmd):
        if self.hierarchy is None or not isinstance(self.hierarchy, dict):
            ColorPrint.exit_after_print_messages("Command hierarchy config is missing")

        if cmd not in self.hierarchy:
            ColorPrint.exit_after_print_messages("Command not found in hierarchy: " + str(cmd))

    def pre_run(self, command_list, plan):
        if command_list.get('before', False):
            self.script_runner.run(plan=plan, script_type='before_script')
        self.run_method('premethods', command_list)

    def after_run(self, command_list, plan):
        self.run_method('postmethods', command_list)
        if command_list.get('after', False):
            self.script_runner.run(plan=plan, script_type='after_script')

    def run_method(self, type, command_list):
        if type in command_list and len(command_list[type]) > 0:
            for method in command_list[type]:
                getattr(self, method)()

    def parse_environment_dict(self, path, env):
        """Compose dictionary from environment variables."""
        file_name = FileUtils.get_compose_file_relative_path(repo_dir=self.repo_dir,
                                                             working_directory=self.working_directory,
                                                             file_name=path)
        env_file = ProjectUtils.get_file(file=file_name)
        if env_file is None:
            ColorPrint.exit_after_print_messages(
                message="Environment file (" + str(file_name) + ") not exists in repository: " + StateHolder.name)
        with open(env_file) as stream:
            for line in stream.readlines():
                if not line.startswith("#"):
                    data = line.split("=", 1)
                    if len(data) > 1:
                        env[data[0].strip()] = data[1].strip()

    def get_environment_dict(self, envs):
        """Process environment files. Environment for selected plan will be override the defaults"""
        environment = dict()
        '''First the default, if exists'''
        if "environment" in self.project_compose:
            self.parse_environment_dict(path=self.project_compose["environment"]["include"], env=environment)
        for env in envs:
            self.parse_environment_dict(path=env, env=environment)
        return environment

    def get_environment_variables(self, plan):
        """Get all environment variables depends on selected plan"""
        envs = list()
        if isinstance(plan, dict):
            if 'environment' in plan and 'include' in plan['environment']:
                    envs.extend(ProjectUtils.get_list_value(plan['environment']['include']))
            if 'docker-compose-dir' in plan:
                envs.extend(FileUtils.get_filtered_sorted_alter_from_base_dir(base_dir=self.repo_dir,
                                                                              actual_dir=self.working_directory,
                                                                              target_directories=ProjectUtils.
                                                                              get_list_value(
                                                                                  plan['docker-compose-dir']),
                                                                              filter_ends='.env'))
        env_dict = self.get_environment_dict(envs=envs)
        env_copy = os.environ.copy()
        for key in env_dict.keys():
            env_copy[key] = env_dict[key]

        """Add host system to environment"""
        env_copy["HOST_SYSTEM"] = platform.system()
        return env_copy

    def pack(self):
        plan = self.project_compose['plan'][self.plan]
        envs = self.get_environment_variables(plan=plan)
        runner = DockerPlanRunner(project_compose=self.project_compose,
                                  working_directory=self.working_directory,
                                  repo_dir=self.repo_dir)
        PackageHandler().pack(files=runner.get_docker_files(plan=plan), envs=envs)

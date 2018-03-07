import os
import yaml
import platform
from subprocess import check_call
from .console_logger import ColorPrint, Doc
from .file_utils import FileUtils
from .project_utils import ProjectUtils
from .environment_utils import EnvironmentUtils
from .package_handler import PackageHandler
from .state import StateHolder


class CommandHandler(object):

    def __init__(self):

        with open(os.path.join(os.path.dirname(__file__), 'resources/command-hierarchy.yml')) as stream:
            try:
                self.hierarchy = yaml.load(stream=stream)
            except yaml.YAMLError as exc:
                ColorPrint.exit_after_print_messages(message="Error: Wrong YAML format:\n " + str(exc),
                                                     doc=Doc.POCOK)

        StateHolder.compose_handler.get_compose_project()
        self.project_compose = StateHolder.compose_handler.compose_project
        self.working_directory = StateHolder.compose_handler.get_working_directory()
        self.plan = StateHolder.compose_handler.plan
        self.repo_dir = StateHolder.repository.target_dir

        ''' Check mode '''
        plan = self.project_compose['plan'][self.plan]
        if isinstance(plan, dict) and ('kubernetes-file' in plan or 'kubernetes-dir' in plan):
            StateHolder.container_mode = "Kubernetes"
        self.script_runner = ScriptPlanRunner(project_compose=self.project_compose,
                                              working_directory=self.working_directory)

        if StateHolder.container_mode == "Docker":
            EnvironmentUtils.check_docker()
        if StateHolder.container_mode == "Kubernetes":
            EnvironmentUtils.check_kubernetes()

    def run_script(self, script):
        self.script_runner.run(plan=self.project_compose['plan'][self.plan], script_type=script)

    def run(self, cmd):

        if self.hierarchy is None or not isinstance(self.hierarchy, dict):
            ColorPrint.exit_after_print_messages("Command hierarchy config is missing")

        if cmd not in self.hierarchy:
            ColorPrint.exit_after_print_messages("Command not found in hierarchy: " + str(cmd))

        plan = self.project_compose['plan'][self.plan]
        command_list = self.hierarchy[cmd]

        if not isinstance(command_list, dict):
            ColorPrint.print_info("Wrong command in hierarchy: " + str(command_list))

        if command_list.get('before', False):
            self.script_runner.run(plan=plan, script_type='before_script')

        if 'premethods' in command_list and len(command_list['premethods']) > 0:
            for method in command_list['premethods']:
                getattr(self, method)()

        if isinstance(plan, dict) and 'script' in plan:
            # script running only if start or up command
            if cmd == 'start' or cmd == 'up':
                self.script_runner.run(plan=plan, script_type='script')
        elif StateHolder.container_mode == 'Kubernetes':
            runner = KubernetesRunner(working_directory=self.working_directory,
                                      repo_dir=self.repo_dir)
            if len(command_list['kubernetes']) == 0:
                ColorPrint.exit_after_print_messages('Command: ' + cmd + ' not supported with Kubernetes')
            for cmd in command_list['kubernetes']:
                runner.run(plan=plan, command=cmd, envs=self.get_environment_variables(plan=plan))
        else:
            runner = DockerPlanRunner(project_compose=self.project_compose,
                                      working_directory=self.working_directory,
                                      repo_dir=self.repo_dir)
            if StateHolder.always_update and cmd is 'start':  # Pull before start in developer mode
                runner.run(plan=plan, commands='pull', envs=self.get_environment_variables(plan=plan))
            for cmd in command_list['docker']:
                runner.run(plan=plan, commands=cmd,
                           envs=self.get_environment_variables(plan=plan))

        if 'postmethods' in command_list and len(command_list['postmethods']) > 0:
            for method in command_list['postmethods']:
                getattr(self, method)()

        if command_list.get('after', False):
            self.script_runner.run(plan=plan, script_type='after_script')

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
            if 'environment' in plan:
                if 'include' in plan['environment']:
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


class AbstractPlanRunner(object):

    @staticmethod
    def run_script_with_check(cmd, working_directory, envs):
        res = check_call(" ".join(cmd), cwd=working_directory, env=envs, shell=True)
        if res > 0:
            ColorPrint.exit_after_print_messages(message=res)


class ScriptPlanRunner(AbstractPlanRunner):

    def __init__(self, project_compose, working_directory):
        self.project_compose = project_compose
        self.working_directory = working_directory

    def run(self, plan, script_type):
        scripts = self.get_native_scripts(plan=plan, script_type=script_type)
        if len(scripts) > 0:
            for script in scripts:
                cmd = self.get_script_base()
                cmd.append("\"")
                cmd.append(script)
                cmd.append("\"")
                self.run_script_with_check(cmd=cmd, working_directory=self.working_directory, envs=os.environ.copy())

    def get_native_scripts(self, plan, script_type):
        """Get scripts """
        scripts = list()
        if not script_type == 'script' and script_type in self.project_compose:
            scripts.extend(ProjectUtils.get_list_value(self.project_compose[script_type]))
        if script_type in plan:
            scripts.extend(ProjectUtils.get_list_value(plan[script_type]))

        return scripts

    def get_script_base(self):
        command_array = list()
        command_array.append("docker")
        command_array.append("run")

        """Add host system to environment"""
        command_array.append("-e")
        command_array.append("HOST_SYSTEM="+platform.system())
        command_array.append("-u")
        command_array.append("1000")
        command_array.append("-v")
        command_array.append(str(self.working_directory) + ":/usr/local")
        command_array.append("-w")
        command_array.append("/usr/local")
        command_array.append("alpine:latest")
        command_array.append("/bin/sh")
        command_array.append("-c")
        return command_array


class KubernetesRunner(AbstractPlanRunner):

    def __init__(self, working_directory, repo_dir):
        self.working_directory = working_directory
        self.repo_dir = repo_dir

    def run(self, plan, command, envs):

        files = list()

        if isinstance(plan, dict) and 'kubernetes-file' in plan:
            for file in ProjectUtils.get_list_value(plan['kubernetes-file']):
                files.append(self.get_file(file=file))
        elif isinstance(plan, dict) and 'kubernetes-dir' in plan:
            files.extend(self.get_list(ProjectUtils.get_list_value(plan['kubernetes-dir'])))

        """Kubernetes commands"""
        for kube_file in files:
            cmd = list()
            cmd.append("kubectl")
            cmd.append(command)
            cmd.append("-f")
            cmd.append(str(kube_file))

            ColorPrint.print_with_lvl(message="Kubernetes command: " + str(cmd), lvl=1)
            self.run_script_with_check(cmd=cmd, working_directory=self.working_directory, envs=envs)

    def get_file(self, file):
        return ProjectUtils.get_file(file=FileUtils.get_compose_file_relative_path(
                                                       repo_dir=self.repo_dir, working_directory=self.working_directory,
                                                       file_name=file))

    def get_list(self, dir_list):
        kube_list = list()
        for file in FileUtils.get_filtered_sorted_alter_from_base_dir(base_dir=self.repo_dir,
                                                                      actual_dir=self.working_directory,
                                                                      target_directories=dir_list,
                                                                      filter_ends=('.yml', '.yaml')):
            kube_list.append(ProjectUtils.get_file(file=file))
        return kube_list


class DockerPlanRunner(AbstractPlanRunner):

    def __init__(self, project_compose, working_directory, repo_dir):
        self.working_directory = working_directory
        self.project_compose = project_compose
        self.repo_dir = repo_dir

    def run(self, plan, commands, envs):

        """Get compose file(s) from config depends on selected plan"""
        docker_files = self.get_docker_files(plan=plan)

        """Compose docker command array with project name and compose files"""
        cmd = list()
        cmd.append("docker-compose")
        cmd.append("--project-name")
        cmd.append(StateHolder.name)
        for compose_file in docker_files:
            cmd.append("-f")
            cmd.append(str(compose_file))

        if type(commands) is list:
            for command in commands:
                cmd.append(command)
        else:
            cmd.append(commands)

        ColorPrint.print_with_lvl(message="Docker command: " + str(cmd), lvl=1)
        self.run_script_with_check(cmd=cmd, working_directory=self.working_directory, envs=envs)

    def get_docker_files(self, plan):
        docker_files = list()
        if isinstance(plan, dict) and 'docker-compose-file' in plan:
            for service in ProjectUtils.get_list_value(plan['docker-compose-file']):
                docker_files.append(self.get_docker_compose(service=service))
        elif isinstance(plan, dict) and 'docker-compose-dir' in plan:
            docker_files.extend(self.get_docker_compose_list(ProjectUtils.get_list_value(plan['docker-compose-dir'])))
        else:
            for service in ProjectUtils.get_list_value(plan):
                docker_files.append(self.get_docker_compose(service=service))

        return docker_files

    def get_docker_compose(self, service):
        """Get back the docker compose file"""
        file_name = self.get_compose_file_name(service=service)
        return ProjectUtils.get_file(file=FileUtils.get_compose_file_relative_path(
                                                       repo_dir=self.repo_dir, working_directory=self.working_directory,
                                                       file_name=file_name))

    def get_docker_compose_list(self, dir_list):
        compose_list = list()
        for file in FileUtils.get_filtered_sorted_alter_from_base_dir(base_dir=self.repo_dir,
                                                                      actual_dir=self.working_directory,
                                                                      target_directories=dir_list,
                                                                      filter_ends=('.yml', '.yaml')):
            compose_list.append(ProjectUtils.get_file(file=file))
        return compose_list

    def get_compose_file_name(self, service):
        """Get back docker compose file name"""
        if self.project_compose is None:
            return service

        if 'containers' in self.project_compose and service in self.project_compose['containers']:
            return self.project_compose['containers'].get(service)
        return service

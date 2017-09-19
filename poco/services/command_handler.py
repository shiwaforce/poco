import os
import yaml
from subprocess import check_call, call
from .console_logger import ColorPrint, Doc
from .file_utils import FileUtils
from .project_utils import ProjectUtils
from .state import StateHolder


class CommandHandler(object):

    def __init__(self, args, compose_handler, project_utils):

        with open(os.path.join(os.path.dirname(__file__), 'resources/command-hierarchy.yml')) as stream:
            try:
                self.hierarchy = yaml.load(stream=stream)
            except yaml.YAMLError as exc:
                ColorPrint.exit_after_print_messages(message="Error: Wrong YAML format:\n " + str(exc),
                                                     doc=Doc.POCO)

        self.args = args
        self.compose_handler = compose_handler
        compose_handler.get_compose_project()
        self.project_compose = self.compose_handler.compose_project
        self.working_directory = self.compose_handler.get_working_directory()
        self.plan = self.compose_handler.plan
        self.repo_dir = self.compose_handler.repo_dir
        self.project_utils = project_utils

        self.script_runner = ScriptPlanRunner(project_compose=self.project_compose,
                                              working_directory=self.working_directory)
        self.docker_runner = DockerPlanRunner(project_compose=self.project_compose,
                                              working_directory=self.working_directory,
                                              project_utils=project_utils,
                                              repo_dir=self.repo_dir)

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

        if isinstance(plan, dict) and 'script' in plan:
            self.script_runner.run(plan=plan, script_type='script')
        else:
            for cmd in command_list['docker']:
                self.docker_runner.run(name=StateHolder.name, plan=plan, commands=cmd,
                                       envs=self.get_environment_variables(plan=plan))

        if command_list.get('after', False):
            self.script_runner.run(plan=plan, script_type='after_script')

    def parse_environment_dict(self, path, env):
        """Compose dictionary from environment variables."""
        file_name = FileUtils.get_compose_file_relative_path(repo_dir=self.repo_dir,
                                                             working_directory=self.working_directory,
                                                             file_name=path)
        env_file = self.project_utils.get_file(file=file_name)
        if env_file is None:
            ColorPrint.exit_after_print_messages(
                message="Environment file (" + str(file_name) + ") not exists in repository: "
                        + StateHolder.name)
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
        if type(envs) is list:
            for env in envs:
                self.parse_environment_dict(path=env, env=environment)
        elif envs is not None:
            self.parse_environment_dict(path=envs, env=environment)
        return environment

    def get_environment_variables(self, plan):
        """Get all environment variables depends on selected plan"""
        envs = None
        if isinstance(plan, dict):
            if 'environment' in plan:
                if 'include' in plan['environment']:
                    envs = plan['environment']['include']
        env_dict = self.get_environment_dict(envs=envs)
        env_copy = os.environ.copy()
        for key in env_dict.keys():
            env_copy[key] = env_dict[key]
        return env_copy


class AbstractPlanRunner(object):

    @staticmethod
    def run_script_with_check(cmd, working_directory):
        res = check_call(args=cmd, cwd=working_directory, shell=True)
        if res > 0:
            ColorPrint.exit_after_print_messages(message=res)

    @staticmethod
    def run_script(cmd, working_directory, envs):
        call(cmd, cwd=working_directory, env=envs, shell=True)


class ScriptPlanRunner(AbstractPlanRunner):

    def __init__(self, project_compose, working_directory):
        self.project_compose = project_compose
        self.working_directory = working_directory

    def run(self, plan, script_type):
        scripts = self.get_native_scripts(plan=plan, script_type=script_type)
        if len(scripts) > 0:
            for script in scripts:
                cmd = self.get_script_base()
                cmd.append(script)
                self.run_script_with_check(cmd=cmd, working_directory=self.working_directory)

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
        command_array.append("-v")
        command_array.append(str(self.working_directory) + ":/usr/local")
        command_array.append("-w")
        command_array.append("/usr/local")
        command_array.append("alpine:latest")
        command_array.append("/bin/sh")
        command_array.append("-c")
        return command_array


class DockerPlanRunner(AbstractPlanRunner):

    def __init__(self, project_compose, working_directory, project_utils, repo_dir):
        self.working_directory = working_directory
        self.project_compose = project_compose
        self.project_utils = project_utils
        self.repo_dir = repo_dir

    def run(self, plan, commands, name, envs):

        """Get compose file(s) from config depends on selected plan"""
        docker_files = list()
        if isinstance(plan, dict) and 'docker-compose-file' in plan:
            for service in ProjectUtils.get_list_value(plan['docker-compose-file']):
                docker_files.append(self.get_docker_compose(service=service, name=name))
        else:
            for service in ProjectUtils.get_list_value(plan):
                docker_files.append(self.get_docker_compose(service=service, name=name))

        """Compose docker command array with project name and compose files"""
        cmd = list()
        cmd.append("docker-compose")
        cmd.append("--project-name")
        cmd.append(name)
        for compose_file in docker_files:
            cmd.append("-f")
            cmd.append(str(compose_file))
        if type(commands) is list:
            for command in commands:
                cmd.append(command)
        else:
            cmd.append(commands)

        ColorPrint.print_with_lvl(message="Docker command: " + str(cmd), lvl=1)
        self.run_script(cmd=cmd, working_directory=self.working_directory, envs=envs)

    def get_docker_compose(self, service, name):
        """Get back the docker compose file"""
        file_name = self.get_compose_file_name(service=service)
        compose_file = self.project_utils.get_file(file=FileUtils.get_compose_file_relative_path(
                                                       repo_dir=self.repo_dir, working_directory=self.working_directory,
                                                       file_name=file_name))
        if compose_file is None:
            ColorPrint.exit_after_print_messages(
                message="Compose file (" + str(file_name) + ") not exists in repository: " + name,
                doc=Doc.COMPOSE_DOC)
        return compose_file

    def get_compose_file_name(self, service):
        """Get back docker compose file name"""
        if self.project_compose is not None:
            if 'containers' in self.project_compose:
                if service in self.project_compose['containers']:
                    return self.project_compose['containers'].get(service)
        return service

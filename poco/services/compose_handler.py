import os
import yaml
from .console_logger import *
from .file_utils import FileUtils
from .project_utils import ProjectUtils
from .state import StateHolder


class ComposeHandler:

    def __init__(self, compose_file, plan, repo_dir):
        self.compose_file = compose_file
        self.compose_project = None
        self.plan = plan
        self.repo_dir = repo_dir

    def get_compose_file_name(self, service):
        """Get back docker compose file name"""
        if self.compose_project is not None:
            if 'containers' in self.compose_project:
                if service in self.compose_project['containers']:
                    return self.compose_project['containers'].get(service)
        return service

    def get_compose_file_relative_path(self, file_name):
        """return the compose file relative path from repository root"""
        return os.path.join(FileUtils.get_relative_path(self.repo_dir, self.get_working_directory()), file_name)

    def get_docker_compose(self, service, get_file):
        """Get back the docker compose file"""
        file_name = self.get_compose_file_name(service=service)
        compose_file = get_file(file=self.get_compose_file_relative_path(file_name=file_name))
        if compose_file is None:
            ColorPrint.exit_after_print_messages(
                message="Compose file (" + str(file_name) + ") not exists in repository: " + StateHolder.name,
                doc=Doc.COMPOSE_DOC)
        return compose_file

    def get_working_directory(self):
        """Get back the working directory if it is set or the project file directory"""
        self.get_compose_project()
        project_directory = os.path.dirname(self.compose_file)
        if 'working-directory' in self.compose_project:
            project_directory = os.path.join(project_directory, self.compose_project['working-directory'])
            if not os.path.exists(project_directory):
                os.mkdir(project_directory)
        return project_directory

    def get_compose_project(self):
        """Load compose file from repository"""
        with open(self.compose_file) as stream:
            try:
                self.compose_project = yaml.load(stream=stream)

                if 'plan' not in self.compose_project:
                    ColorPrint.exit_after_print_messages(
                        message="'plan' section must exists in compose file (poco.yml) ",
                        doc=Doc.COMPOSE_DOC)
                if not isinstance(self.compose_project['plan'], dict):
                    ColorPrint.exit_after_print_messages(
                        message="'plan' section must be a list", doc=Doc.POCO)
                if len(self.compose_project['plan'].keys()) < 1:
                    ColorPrint.exit_after_print_messages(
                        message="'plan' section must be one child element", doc=Doc.POCO)
                if self.plan is None:
                    if "demo" in self.compose_project['plan']:
                        self.plan = "demo"
                    elif "default" in self.compose_project['plan']:
                        self.plan = "default"
                    else:
                        self.plan = self.compose_project['plan'].keys()[0]
                if self.plan not in self.compose_project['plan']:
                    ColorPrint.exit_after_print_messages(
                        message="stages section must contains the selected stage: " + str(self.plan), doc=Doc.POCO)

                actual_plan = self.compose_project['plan'].get(self.plan)
                if actual_plan is None:
                    ColorPrint.exit_after_print_messages(
                        message="selected plan %s is empty" % str(self.plan), msg_type="warn", doc=Doc.POCO)
            except yaml.YAMLError as exc:
                ColorPrint.exit_after_print_messages(message="Error: Wrong YAML format:\n " + str(exc),
                                                     doc=Doc.POCO)

    def parse_environment_dict(self, path, env, get_file):
        """Compose dictionary from environment variables."""
        file_name = self.get_compose_file_relative_path(file_name=path)
        env_file = get_file(file=file_name)
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

    def get_environment_dict(self, envs, get_file):
        """Process environment files. Environment for selected plan will be override the defaults"""
        environment = dict()
        '''First the default, if exists'''
        if "environment" in self.compose_project:
            self.parse_environment_dict(path=self.compose_project["environment"]["include"], env=environment,
                                        get_file=get_file)
        if type(envs) is list:
            for env in envs:
                self.parse_environment_dict(path=env, env=environment, get_file=get_file)
        elif envs is not None:
            self.parse_environment_dict(path=envs, env=environment, get_file=get_file)
        return environment

    def get_environment_variables(self, get_file):
        """Get all environment variables depends on selected plan"""
        selected_type = self.compose_project['plan'].get(self.plan)
        envs = None
        if isinstance(selected_type, dict):
            if 'environment' in selected_type:
                if 'include' in selected_type['environment']:
                    envs = selected_type['environment']['include']
        env_dict = self.get_environment_dict(envs=envs, get_file=get_file)
        env_copy = os.environ.copy()
        for key in env_dict.keys():
            env_copy[key] = env_dict[key]
        return env_copy

    def get_compose_files(self, get_file):
        """Get compose file(s) from config depends on selected plan"""
        self.get_compose_project()
        selected_type = self.compose_project['plan'].get(self.plan)
        docker_files = list()
        if isinstance(selected_type, dict) and 'docker-compose-file' in selected_type:
            for service in ProjectUtils.get_list_value(selected_type['docker-compose-file']):
                docker_files.append(self.get_docker_compose(service=service, get_file=get_file))
        else:
            for service in ProjectUtils.get_list_value(selected_type):
                docker_files.append(self.get_docker_compose(service=service, get_file=get_file))
        return docker_files

    def get_command(self, commands, get_file):
        """Compose docker command array with project name and compose files"""
        command_array = list()
        command_array.append("docker-compose")
        command_array.append("--project-name")
        command_array.append(StateHolder.name)
        for compose_file in self.get_compose_files(get_file=get_file):
            command_array.append("-f")
            command_array.append(str(compose_file))
        if type(commands) is list:
            for command in commands:
                command_array.append(command)
        else:
            command_array.append(commands)
        return command_array

    def get_checkouts(self):
        """Get checkouts list from compose file"""
        self.get_compose_project()
        checkouts = list()
        if 'checkout' in self.compose_project:
            checkouts = ProjectUtils.get_list_value(self.compose_project['checkout'])
        if 'checkout' in self.compose_project['plan'][self.plan]:
            checkouts.extend(ProjectUtils.get_list_value(self.compose_project['plan'][self.plan]['checkout']))
        return checkouts

    def get_plan_list(self):
        """Print all available plan from project compose file"""
        self.get_compose_project()
        ColorPrint.print_with_lvl(message="---------------------------------------------------------------", lvl=-1)
        ColorPrint.print_with_lvl(message="Available plans for project: " + str(StateHolder.name), lvl=-1)
        ColorPrint.print_with_lvl(message="---------------------------------------------------------------", lvl=-1)

        for key in self.compose_project['plan'].keys():
            ColorPrint.print_with_lvl(message=key, lvl=-1)


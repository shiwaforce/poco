import os
import yaml
from .console_logger import *
from .file_utils import FileUtils


class ComposeHandler:

    def __init__(self, compose_file, mode, repo_dir):
        self.compose_file = compose_file
        self.compose_project = None
        self.mode = mode
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

    def get_docker_compose(self, service, name, get_file):
        """Get back the docker compose file"""
        file_name = self.get_compose_file_name(service=service)
        compose_file = get_file(name=name,
                                file=self.get_compose_file_relative_path(file_name=file_name))
        if compose_file is None:
            ColorPrint.exit_after_print_messages(
                message="Compose file (" + str(file_name) + ") not exists in repository: " + name,
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

                if 'mode' not in self.compose_project:
                    ColorPrint.exit_after_print_messages(
                        message="'mode' section must exists in compose file (project-compose.yml) ",
                        doc=Doc.COMPOSE_DOC)
                if not isinstance(self.compose_project['mode'], dict):
                    ColorPrint.exit_after_print_messages(
                        message="'mode' section must be a list", doc=Doc.PROJECT_COMPOSE)
                if len(self.compose_project['mode'].keys()) < 1:
                    ColorPrint.exit_after_print_messages(
                        message="'mode' section must be one child element", doc=Doc.PROJECT_COMPOSE)
                if self.mode is None:
                    if "demo" in self.compose_project['mode']:
                        self.mode = "demo"
                    elif "default" in self.compose_project['mode']:
                        self.mode = "default"
                    else:
                        self.mode = self.compose_project['mode'].keys()[0]
                if self.mode not in self.compose_project['mode']:
                    ColorPrint.exit_after_print_messages(
                        message="stages section must contains the selected stage: " + str(self.mode), doc=Doc.PROJECT_COMPOSE)

                actual_mode = self.compose_project['mode'].get(self.mode)
                if actual_mode is None:
                    ColorPrint.exit_after_print_messages(
                        message="selected mode %s is empty" % str(self.mode), msg_type="warn", doc=Doc.PROJECT_COMPOSE)
            except yaml.YAMLError as exc:
                ColorPrint.exit_after_print_messages(message="Error: Wrong YAML format:\n " + str(exc),
                                                     doc=Doc.PROJECT_COMPOSE)

    def parse_environment_dict(self, path, env, name, get_file):
        """Compose dictionary from environment variables."""
        file_name = self.get_compose_file_relative_path(file_name=path)
        env_file = get_file(name=name, file=file_name)
        if env_file is None:
            ColorPrint.exit_after_print_messages(
                message="Environment file (" + str(file_name) + ") not exists in repository: "
                        + name)
        with open(env_file) as stream:
            for line in stream.readlines():
                if not line.startswith("#"):
                    data = line.split("=", 1)
                    if len(data) > 1:
                        env[data[0].strip()] = data[1].strip()

    def get_environment_dict(self, envs, name, get_file):
        """Process environment files. Environment for selected mode will be override the defaults"""
        environment = dict()
        '''First the default, if exists'''
        if "environment" in self.compose_project:
            self.parse_environment_dict(path=self.compose_project["environment"]["include"], env=environment,
                                        name=name, get_file=get_file)
        if (type(envs) is list):
            for env in envs:
                self.parse_environment_dict(path=env, env=environment, name=name, get_file=get_file)
        elif envs is not None:
            self.parse_environment_dict(path=envs, env=environment, name=name, get_file=get_file)
        return environment

    def get_environment_variables(self, name, get_file):
        """Get all environment variables depends on selected mode"""
        selected_type = self.compose_project['mode'].get(self.mode)
        envs = None
        if isinstance(selected_type, dict):
            if 'environment' in selected_type:
                if 'include' in selected_type['environment']:
                    envs = selected_type['environment']['include']
        env_dict = self.get_environment_dict(envs=envs, name=name, get_file=get_file)
        env_copy = os.environ.copy()
        for key in env_dict.keys():
            env_copy[key] = env_dict[key]
        return env_copy

    def get_compose_files(self, name, get_file):
        """Get compose file(s) from config depends on selected mode"""
        self.get_compose_project()
        selected_type = self.compose_project['mode'].get(self.mode)
        docker_files = list()
        if isinstance(selected_type, dict) and 'docker-compose-file' in selected_type:
            for service in self.get_list_value(selected_type['docker-compose-file']):
                docker_files.append(self.get_docker_compose(service=service, name=name, get_file=get_file))
        else:
            for service in self.get_list_value(selected_type):
                docker_files.append(self.get_docker_compose(service=service, name=name, get_file=get_file))
        return docker_files

    def get_command(self, commands, name, get_file):
        """Compose docker command array with project name and compose files"""
        command_array = list()
        command_array.append("docker-compose")
        command_array.append("--project-name")
        command_array.append(name)
        for compose_file in self.get_compose_files(name=name, get_file=get_file):
            command_array.append("-f")
            command_array.append(str(compose_file))
        if type(commands) is list:
            for command in commands:
                command_array.append(command)
        else:
            command_array.append(commands)
        return command_array

    def get_scripts(self, script_type):
        """Get scripts """
        self.get_compose_project()
        scripts = list()
        if script_type in self.compose_project:
            scripts = self.get_list_value(self.compose_project[script_type])
        return scripts

    def get_after_scripts(self):
        """Get after scripts """
        self.get_compose_project()
        scripts = list()
        if 'after_script' in self.compose_project:
            scripts = self.get_list_value(self.compose_project['after_script'])
        return scripts

    def get_init_scripts(self):
        """Get install scripts """
        self.get_compose_project()
        scripts = list()
        if 'init_scripts' in self.compose_project:
            scripts = self.get_list_value(self.compose_project['init_scripts'])
        return scripts

    def get_remove_scripts(self):
        """Get uninstall scripts """
        self.get_compose_project()
        scripts = list()
        if 'remove_scripts' in self.compose_project:
            scripts = self.get_list_value(self.compose_project['remove_scripts'])
        return scripts

    def get_checkouts(self):
        """Get checkouts list from compose file"""
        self.get_compose_project()
        checkouts = list()
        if 'checkout' in self.compose_project:
            checkouts = self.get_list_value(self.compose_project['checkout'])
        return checkouts

    def get_mode_list(self, name):
        """Print all available mode from project compose file"""
        self.get_compose_project()
        ColorPrint.print_with_lvl(message="---------------------------------------------------------------", lvl=-1)
        ColorPrint.print_with_lvl(message="Available modes for project: " + str(name), lvl=-1)
        ColorPrint.print_with_lvl(message="---------------------------------------------------------------", lvl=-1)

        for key in self.compose_project['mode'].keys():
            ColorPrint.print_with_lvl(message=key, lvl=-1)

    @staticmethod
    def get_list_value(value):
        """Get list format, doesn't matter the config use one or list mode"""
        lst = list()
        if (type(value) is list):
            lst.extend(value)
        else:
            lst.append(value)
        return lst

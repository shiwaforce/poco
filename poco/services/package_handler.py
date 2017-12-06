import os
import platform
import shutil
import tarfile
from subprocess import check_output, check_call
from .console_logger import ColorPrint
from .environment_utils import EnvironmentUtils
from .project_utils import ProjectUtils
from .file_utils import FileUtils
from .state import StateHolder
from .yaml_handler import YamlHandler

""" Proof of Concept, I know, it's ugly and duplicated"""


class PackageHandler(object):

    repo_dir = None
    working_directory = None
    project_utils = None
    project_compose = None

    def pack(self, compose_handler, project_utils):
        EnvironmentUtils.check_docker()
        compose_handler.get_compose_project()
        self.repo_dir = compose_handler.repo_dir
        self.working_directory = compose_handler.get_working_directory()

        self.project_compose = compose_handler.compose_project
        self.project_utils = project_utils
        docker_files = list()
        plan = self.project_compose['plan'][compose_handler.plan]
        if isinstance(plan, dict):
            if 'kubernetes-file' in plan or 'kubernetes-dir' in plan or 'script' in plan:
                ColorPrint.exit_after_print_messages("Package only support Docker files")
        if isinstance(plan, dict) and 'docker-compose-file' in plan:
            for service in ProjectUtils.get_list_value(plan['docker-compose-file']):
                docker_files.append(self.get_docker_compose(service=service))
        elif isinstance(plan, dict) and 'docker-compose-dir' in plan:
            docker_files.extend(self.get_docker_compose_list(ProjectUtils.get_list_value(plan['docker-compose-dir'])))
        else:
            for service in ProjectUtils.get_list_value(plan):
                docker_files.append(self.get_docker_compose(service=service))

        if not os.path.exists(os.path.join(self.working_directory, "tmp_archive")):
            os.mkdir(os.path.join(self.working_directory, "tmp_archive"))

        target_file = os.path.join(self.working_directory, StateHolder.name + ".poco")
        images_file = os.path.join(self.working_directory, "tmp_archive", StateHolder.name + ".tar")
        compose_file = os.path.join(self.working_directory, "tmp_archive", "docker-compose.yml")
        poco_file = os.path.join(self.working_directory, "tmp_archive", "poco.yml")
        images = self.get_images(docker_files)

        cmd = self.get_compose_base_cmd(docker_files=docker_files)
        cmd.append("pull")
        res = check_call(" ".join(cmd), env=self.get_environment_variables(plan=plan), cwd=self.working_directory,
                         shell=True)
        if res > 0:
            ColorPrint.exit_after_print_messages(message=res)

        cmd = self.get_compose_base_cmd(docker_files=docker_files)
        cmd.append("config")
        res = EnvironmentUtils.decode(check_output(" ".join(cmd), env=self.get_environment_variables(plan=plan),
                                                   cwd=self.working_directory, shell=True))

        with open(compose_file, 'w') as stream:
            stream.write(res.replace(str(self.working_directory), "."))

        src_file = os.path.join(os.path.dirname(__file__), 'resources/poco.yml')
        shutil.copyfile(src=src_file, dst=poco_file)

        cmd = list()
        cmd.append("docker")
        cmd.append("save")
        cmd.append("-o")
        cmd.append(images_file)
        for image in images:
            cmd.append(str(image))
        res = check_call(" ".join(cmd), cwd=self.working_directory, shell=True)
        if res > 0:
            ColorPrint.exit_after_print_messages(message=res)

        with tarfile.open(target_file, "w:gz") as tar:
            tar.add(os.path.join(self.working_directory, "tmp_archive"), arcname='.')

        shutil.rmtree(os.path.join(self.working_directory, "tmp_archive"))
        ColorPrint.print_info(message='Docker environment save to ' + target_file)

    def unpack(self):
        EnvironmentUtils.check_docker()
        pocofile = None
        for file in next(os.walk(os.getcwd()))[2]:
            if file.endswith(".poco"):
                pocofile = file
                tar = tarfile.open(file)
                tar.extractall()
                tar.close()
                break
        if pocofile is None:
            ColorPrint.exit_after_print_messages(message=".poco file not exists in current directory")

        cmd = list()
        cmd.append("docker")
        cmd.append("load")
        cmd.append("-i")
        cmd.append(pocofile.rstrip("poco") + "tar")
        self.run_script(cmd=cmd)

    def up(self):
        cmd = list()
        cmd.append("docker-compose")
        cmd.append("--project-name")
        cmd.append(FileUtils.get_directory_name())
        cmd.append("up")
        cmd.append("-d")
        self.run_script(cmd=cmd)

    def down(self):
        cmd = list()
        cmd.append("docker-compose")
        cmd.append("down")
        self.run_script(cmd=cmd)

    def get_compose_base_cmd(self, docker_files):
        cmd = list()
        cmd.append("docker-compose")
        for compose_file in docker_files:
            cmd.append("-f")
            cmd.append(str(compose_file))
        return cmd

    def run_script(self, cmd):
        res = check_call(" ".join(cmd), cwd=self.working_directory, shell=True)
        if res > 0:
            ColorPrint.exit_after_print_messages(message=res)

    def get_docker_compose(self, service):
        """Get back the docker compose file"""
        file_name = self.get_compose_file_name(service=service)
        return self.project_utils.get_file(file=FileUtils.get_compose_file_relative_path(
            repo_dir=self.repo_dir, working_directory=self.working_directory,
            file_name=file_name))

    def get_docker_compose_list(self, dir_list):
        compose_list = list()
        for file in FileUtils.get_filtered_sorted_alter_from_base_dir(base_dir=self.repo_dir,
                                                                      actual_dir=self.working_directory,
                                                                      target_directories=dir_list,
                                                                      filter_ends=('.yml', '.yaml')):
            compose_list.append(self.project_utils.get_file(file=file))
        return compose_list

    def get_compose_file_name(self, service):
        """Get back docker compose file name"""
        if self.project_compose is not None:
            if 'containers' in self.project_compose:
                if service in self.project_compose['containers']:
                    return self.project_compose['containers'].get(service)
        return service

    def get_images(self, docker_files):
        res = list()
        for docker_file in docker_files:
            res.extend(self.get_image(docker_file))
        return set(res)

    def get_image(self, docker_file):
        res = list()
        compose_content = YamlHandler.read(docker_file)
        for serv in compose_content['services']:
            service = compose_content['services'][serv]
            if isinstance(service, dict) and 'image' in service:
                res.append(service['image'])
        return res

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
import os
import platform
from subprocess import check_call, CalledProcessError
from .console_logger import ColorPrint
from .file_utils import FileUtils
from .project_utils import ProjectUtils
from .state import StateHolder


class AbstractPlanRunner(object):

    @staticmethod
    def run_script_with_check(cmd, working_directory, envs):
        res = check_call(" ".join(cmd), cwd=working_directory, env=envs, shell=True)
        if res > 0:
            ColorPrint.exit_after_print_messages(message=res)

    @staticmethod
    def get_file_list(base_dir, working_dir, dir_list):
        file_list = list()
        for file in FileUtils.get_filtered_sorted_alter_from_base_dir(base_dir=base_dir,
                                                                      actual_dir=working_dir,
                                                                      target_directories=dir_list,
                                                                      filter_ends=('.yml', '.yaml')):
            file_list.append(ProjectUtils.get_file(file=file))
        return file_list

    @staticmethod
    def get_file(repo_dir, working_directory, file):
        return ProjectUtils.get_file(file=FileUtils.get_compose_file_relative_path(
                                                       repo_dir=repo_dir, working_directory=working_directory,
                                                       file_name=file))

    @staticmethod
    def get_files_list(plan, repo_dir, working_directory):
        files = list()
        if isinstance(plan, dict) and 'kubernetes-file' in plan:
            for file in ProjectUtils.get_list_value(plan['kubernetes-file']):
                files.append(AbstractPlanRunner.get_file(repo_dir=repo_dir, working_directory=working_directory,
                                                         file=file))
        return files


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
        if not platform.system() == 'Windows':
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

    def run(self, plan, commands, envs):
        files = AbstractPlanRunner.get_files_list(plan=plan, repo_dir=self.repo_dir,
                                                  working_directory=self.working_directory)
        if isinstance(plan, dict) and len(files) == 0 and 'kubernetes-dir' in plan:
            files.extend(self.get_file_list(self.repo_dir, self.working_directory,
                                            ProjectUtils.get_list_value(plan['kubernetes-dir'])))

        """Kubernetes commands"""
        for kube_file in files:
            cmd = list()
            cmd.append("kubectl")
            cmd.extend(ProjectUtils.get_list_value(commands))
            cmd.append("-f")
            cmd.append(str(kube_file))

            ColorPrint.print_with_lvl(message="Kubernetes command: " + str(cmd), lvl=1)
            self.run_script_with_check(cmd=cmd, working_directory=self.working_directory, envs=envs)


class HelmRunner(AbstractPlanRunner):

    def __init__(self, working_directory, repo_dir):
        self.working_directory = working_directory
        self.repo_dir = repo_dir

    def run(self, plan, commands, envs):
        files = AbstractPlanRunner.get_files_list(plan=plan, repo_dir=self.repo_dir,
                                                  working_directory=self.working_directory)
        dirs = list()
        if isinstance(plan, dict) and 'helm-dir' in plan:
            directories = ProjectUtils.get_list_value(plan['helm-dir'])
            if len(directories) > 1:
                ColorPrint.print_with_lvl(message="Helm plan use only the first directory from helm-dir")
            dirs.append(os.path.join(FileUtils.get_relative_path(self.repo_dir, self.working_directory),
                                     directories[0]))

        """Helm command"""

        cmd = list()
        cmd.append("helm")
        cmd.extend(ProjectUtils.get_list_value(commands))
        cmd.append("poco-" + StateHolder.name)

        HelmRunner.build_command(cmd=cmd, dirs=dirs, files=files)
        ColorPrint.print_with_lvl(message="Helm command: " + str(cmd), lvl=1)
        try:
            self.run_script_with_check(cmd=cmd, working_directory=self.working_directory, envs=envs)
        except CalledProcessError:
            pass

    @staticmethod
    def build_command(cmd, dirs, files):
        if "install" in cmd or "upgrade" in cmd:
            if len(dirs) > 0:
                cmd.append(str(dirs[0]))
            for file in files:
                cmd.append("-f")
                cmd.append(str(file))


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
        cmd.extend(ProjectUtils.get_list_value(commands))
        ColorPrint.print_with_lvl(message="Docker command: " + str(cmd), lvl=1)
        self.run_script_with_check(cmd=cmd, working_directory=self.working_directory, envs=envs)

    def get_docker_files(self, plan):
        docker_files = list()
        if isinstance(plan, dict) and 'docker-compose-file' in plan:
            self.parse_file_list(ProjectUtils.get_list_value(plan['docker-compose-file']), docker_files)
        elif isinstance(plan, dict) and 'docker-compose-dir' in plan:
            docker_files.extend(self.get_file_list(self.repo_dir, self.working_directory,
                                                   ProjectUtils.get_list_value(plan['docker-compose-dir'])))
        else:
            self.parse_file_list(ProjectUtils.get_list_value(plan), docker_files)
        return docker_files

    def parse_file_list(self, services, docker_files):
        for service in services:
            docker_files.append(self.get_docker_compose(service=service))

    def get_docker_compose(self, service):
        """Get back the docker compose file"""
        file_name = self.get_compose_file_name(service=service)
        return ProjectUtils.get_file(file=FileUtils.get_compose_file_relative_path(
                                                       repo_dir=self.repo_dir, working_directory=self.working_directory,
                                                       file_name=file_name))

    def get_compose_file_name(self, service):
        """Get back docker compose file name"""
        if self.project_compose is None:
            return service

        if 'containers' in self.project_compose and service in self.project_compose['containers']:
            return self.project_compose['containers'].get(service)
        return service

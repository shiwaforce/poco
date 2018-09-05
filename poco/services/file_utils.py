import datetime
import git
import os
import yaml
import stat
from .console_logger import ColorPrint
from .state import StateHolder


class FileUtils:

    @staticmethod
    def make_empty_file(directory, file):
        file = os.path.join(directory, file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(file):
            with open(file, 'w') as stream:
                stream.write(" ")

    @staticmethod
    def make_empty_file_with_empty_dict(directory, file):
        file = os.path.join(directory, file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(file):
            with open(file, 'w') as stream:
                content = dict()
                stream.write(yaml.dump(data=content, default_flow_style=False))

    @staticmethod
    def get_directory_name():
        return os.path.basename(os.getcwd())

    @staticmethod
    def get_relative_path(base_path, target_path):
        return os.path.relpath(path=target_path, start=os.path.commonprefix([target_path, base_path])) + "/"

    @staticmethod
    def get_git_repo(base_dir):
        if not os.path.isdir(base_dir):
            ColorPrint.exit_after_print_messages(message="Target directory is not a valid git repository: " + base_dir)
        try:
            repo = git.Repo(base_dir)
            return repo, base_dir
        except git.exc.InvalidGitRepositoryError as exc:
            if base_dir == os.path.dirname(base_dir):
                ColorPrint.exit_after_print_messages(message="Target directory or parents are"
                                                             " not a valid git repository")
            return FileUtils.get_git_repo(os.path.dirname(base_dir))

    @staticmethod
    def get_compose_file_relative_path(repo_dir, working_directory, file_name):
        """return the compose file relative path from repository root"""
        return os.path.join(FileUtils.get_relative_path(repo_dir, working_directory), file_name)

    @staticmethod
    def get_file_path(repo_dir, working_directory, file_name):
        """return the compose file relative path from repository root"""
        return os.path.join(repo_dir, FileUtils.get_relative_path(repo_dir, working_directory), file_name)

    @staticmethod
    def remove_readonly(func, path):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    @staticmethod
    def get_filtered_sorted_alter_from_base_dir(base_dir, actual_dir, target_directories=list(), filter_ends=list()):
        file_list = list()
        files_dict = FileUtils.get_files_dict_from_directory(base_dir, actual_dir,
                                                             target_directories=target_directories,
                                                             filter_ends=filter_ends)
        for key in files_dict.keys():
            for work_dir in files_dict[key]:
                file_list.append(FileUtils.get_compose_file_relative_path(
                    repo_dir=base_dir, working_directory=work_dir, file_name=key))
        return file_list

    @staticmethod
    def get_files_dict_from_directory(base_dir, actual_dir, target_directories, filter_ends):
        files_dict = dict()
        for directory in target_directories:
            for root, sub_folders, files in os.walk(os.path.join(base_dir, FileUtils.get_file_path(
                    repo_dir=base_dir, working_directory=actual_dir, file_name=directory))):
                FileUtils.filter_and_add_to_dict(files_dict, filter_ends, root, files)
        return files_dict

    @staticmethod
    def filter_and_add_to_dict(files_dict, filter_ends, root, files):
        if len(filter_ends) > 0:
            files = [file for file in files if file.endswith(tuple(filter_ends))]
        for file in files:
            if file not in files_dict.keys():
                files_dict[file] = list()
                files_dict[file].append(root)

    @staticmethod
    def get_parameter_or_directory_name(param):
        arg = StateHolder.args.get(param)
        return arg if arg is not None else FileUtils.get_directory_name()

    @staticmethod
    def get_file_with_extension(file, directory=None, extensions=None):
        if extensions is None:
            extensions = ['yml', 'yaml']
        directory = os.getcwd() if directory is None else directory
        file_lists = os.listdir(directory)
        for ext in extensions:
            if file + "." + ext in file_lists:
                return os.path.join(directory, file + "." + ext)
        return None

    # TODO remove later
    @staticmethod
    def get_backward_compatible_poco_file(directory=None, throw_exception=False, silent=False):
        file = FileUtils.get_file_with_extension(file="poco", directory=directory)
        if file is not None:
            return file

        file = FileUtils.get_file_with_extension(file="pocok", directory=directory)
        if file is None:
            file = FileUtils.get_file_with_extension(file="proco", directory=directory)
        if file is not None:
            if not silent:
                ColorPrint.print_info("Your configuration file (" + file +
                                      ") is deprecated! Use 'poco.yaml/yml' instead.")
            return file
        if throw_exception:
            ColorPrint.exit_after_print_messages("Directory not contains Poco file!")

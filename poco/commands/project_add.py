import os
from .abstract_command import AbstractCommand
from ..services.console_logger import ColorPrint
from ..services.catalog_handler import CatalogHandler
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.file_utils import FileUtils


class ProjectAdd(AbstractCommand):

    sub_command = "project"
    command = "add"
    args = ["[<target-dir>]", "[<catalog>]"]
    args_descriptions = {"[<target-dir>]": "Target directory that will be added to the catalog. "
                                           "(default: current directory)",
                         "[<catalog>]": "Name of the catalog. (default: name with default or first)"}
    description = "Run: 'poco project add . default' to add actual directory to default catalog."

    def __init__(self):
        super(ProjectAdd, self).__init__()
        self.target_dir = None
        self.repo = None
        self.repo_name = None
        self.file = None

    def prepare_states(self):
        StateUtils.prepare("catalog")
        self.get_normalized_dir()

    def resolve_dependencies(self):

        if not os.path.exists(self.target_dir) or not os.path.isdir(self.target_dir):
            ColorPrint.exit_after_print_messages(message=self.target_dir + " is not a directory")

        self.repo, repo_dir = FileUtils.get_git_repo(self.target_dir)
        directory = None
        if self.target_dir != repo_dir:
            directory = FileUtils.get_relative_path(base_path=repo_dir, target_path=self.target_dir)
            self.repo_name = os.path.basename(repo_dir)
        file_name = FileUtils.get_backward_compatible_poco_file(self.target_dir, True)
        file_name = FileUtils.get_relative_path(base_path=self.target_dir, target_path=file_name).rstrip('/')
        self.file = file_name if directory is None else directory + file_name

    def execute(self):
        CatalogHandler.add_to_list(name=os.path.basename(os.path.abspath(self.target_dir)),
                                   url=self.repo.remotes.origin.url, file=self.file, repo_name=self.repo_name)
        ColorPrint.print_info("Project added")

    def get_normalized_dir(self):
        target_dir = StateHolder.args.get('<target-dir>')
        if target_dir is not None:
            if not os.path.exists(target_dir):
                if os.path.exists(os.path.join(os.getcwd(), target_dir)):
                    target_dir = os.path.join(os.getcwd(), target_dir)
        else:
            target_dir = os.getcwd()
        self.target_dir = os.path.normpath(target_dir)

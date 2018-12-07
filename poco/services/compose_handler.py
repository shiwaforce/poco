import os
import yaml
from .console_logger import *
from .git_repository import GitRepository
from .project_utils import ProjectUtils
from .state import StateHolder
from .yaml_utils import YamlUtils


class ComposeHandler:

    def __init__(self, compose_file):
        self.compose_file = compose_file
        self.plan = StateHolder.plan
        self.compose_project = None

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
        if self.compose_project is not None:
            return
        with open(self.compose_file) as stream:
            try:
                self.compose_project = YamlUtils.ordered_load(stream, yaml.SafeLoader)

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
                        self.plan = list(self.compose_project['plan'].keys())[0]
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

    @staticmethod
    def run_checkouts():
        for checkout in StateHolder.compose_handler.get_checkouts():
            if " " not in checkout:
                ColorPrint.exit_after_print_messages(message="Wrong checkout command: " + checkout)
            directory, repository = checkout.split(" ")
            target_dir = os.path.join(StateHolder.compose_handler.get_working_directory(), directory)
            if not StateHolder.offline:
                GitRepository(target_dir=target_dir, url=repository, branch="master")
            if not os.path.exists(target_dir):
                ColorPrint.exit_after_print_messages("checkout directory is empty: " + str(directory))

    def get_checkouts(self):
        """Get checkouts list from compose file"""
        self.get_compose_project()
        checkouts = list()
        if 'checkout' in self.compose_project:
            checkouts = ProjectUtils.get_list_value(self.compose_project['checkout'])
        if 'checkout' in self.compose_project['plan'][self.plan]:
            checkouts.extend(ProjectUtils.get_list_value(self.compose_project['plan'][self.plan]['checkout']))
        return checkouts

    def have_script(self, script):
        """Get checkouts list from compose file"""
        self.get_compose_project()
        if script in self.compose_project:
            return True
        if 'checkout' in self.compose_project['plan'][self.plan]:
            return True
        return False

    def get_plan_list(self):
        """Print all available plan from project compose file"""
        self.get_compose_project()
        ColorPrint.print_with_lvl(message="---------------------------------------------------------------", lvl=-1)
        ColorPrint.print_with_lvl(message="Available plans for project: " + str(StateHolder.name), lvl=-1)
        ColorPrint.print_with_lvl(message="---------------------------------------------------------------", lvl=-1)

        for key in self.compose_project['plan'].keys():
            ComposeHandler.print_message(key=key, plan=self.compose_project['plan'][key])

    @staticmethod
    def print_message(key, plan):
        if isinstance(plan, dict) and 'description' in plan:
            ColorPrint.print_with_lvl(message=key + "\t\t" + plan['description'], lvl=-1)
        else:
            ColorPrint.print_with_lvl(message=key, lvl=-1)

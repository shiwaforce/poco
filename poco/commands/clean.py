from subprocess import check_output, CalledProcessError
from .abstract_command import AbstractCommand
from ..services.console_logger import ColorPrint
from ..services.environment_utils import EnvironmentUtils
from ..services.project_utils import ProjectUtils


class Clean(AbstractCommand):

    command = "clean"
    description = "Run: 'poco clean' to clean all containers and images from local Docker repository."

    def prepare_states(self):
        """ Nothing need """
        pass

    def resolve_dependencies(self):
        """ Check Docker """
        EnvironmentUtils.check_docker()

    def execute(self):
        self.check_container(status="created")
        self.check_container(status="exited")
        self.check_images()
        self.check_volumes()
        ColorPrint.print_info(message="Clean complete")

    def check_container(self, status):
        out = check_output(" ".join(["docker", "ps", "-qf", "status=" + str(status)]), shell=True)

        if len(out) == 0:
            ColorPrint.print_warning('No "' + str(status) + '" containers to remove.')
        else:
            ColorPrint.print_info("=== clean unused containers  ===")
            ColorPrint.print_with_lvl(message="Remove containers:\n" + str(out), lvl=1)
            try:
                self.checkout("docker", "rm", EnvironmentUtils.decode(out).strip().splitlines())
            except CalledProcessError as grepexc:
                self.print_error(grepexc)

    def check_images(self):
        out = check_output(" ".join(["docker", "images", "-q"]), shell=True)
        if len(out) == 0:
            ColorPrint.print_warning('No images to remove.')
        else:
            ColorPrint.print_info("=== clean unused images  ===")
            ColorPrint.print_with_lvl(message="Remove images:\n" + str(out), lvl=1)
            try:
                self.checkout("docker", "rmi", "-f", EnvironmentUtils.decode(out).strip().splitlines())
            except CalledProcessError as grepexc:
                self.print_error(grepexc)

    def check_volumes(self):
        out = check_output(" ".join(["docker", "volume", "ls", "-q"]), shell=True)
        if len(out) == 0:
            ColorPrint.print_warning('No volumes to remove.')
        else:
            ColorPrint.print_info("=== clean unused volumes  ===")
            ColorPrint.print_with_lvl(message="Remove volumes:\n" + str(out), lvl=1)
            self.checkout("docker", "volume", "rm", EnvironmentUtils.decode(out).splitlines())

    def checkout(self, *args):
        command_array = list()
        for cnt, command in enumerate(args):
            command_array.extend(ProjectUtils.get_list_value(command))
        try:
            check_output(" ".join(command_array), shell=True)
        except CalledProcessError as grepexc:
            self.print_error(grepexc)

    @staticmethod
    def print_error(exc):
        ColorPrint.print_error(
            "error code: " + str(exc.returncode) + " with output: " + str(exc.output))

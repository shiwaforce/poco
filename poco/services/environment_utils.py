import os
import sys
from subprocess import Popen, PIPE
from .console_logger import ColorPrint


class EnvironmentUtils:

    @staticmethod
    def get_variable(key, default=None):
        return os.environ.get(key, default)

    @staticmethod
    def check_docker():
        p = Popen("docker version -f {{.Server.Version}}", stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        if not len(err) == 0 or len(out) == 0:
            ColorPrint.exit_after_print_messages(message='Docker not running.')
        if str(out).split(".")[0] < str(17):
            ColorPrint.exit_after_print_messages(message='Please upgrade Docker to version 17 or above')

    @staticmethod
    def check_kubernetes():
        EnvironmentUtils.check_base(command="kubectl version --short", message_head="Kubernetes")

    @staticmethod
    def check_helm():
        EnvironmentUtils.check_base(command="helm version -s --short", message_head="Helm")

    @staticmethod
    def check_base(command, message_head):
        p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        if not len(err) == 0 or len(out) == 0:
            ColorPrint.exit_after_print_messages(message=str(err).strip())
        ColorPrint.print_with_lvl(message=message_head + "\n " + str(out).strip(), lvl=1)

    @staticmethod
    def check_version(version):

        newest_version = "0.0.0"
        # check pip
        p = Popen("pip install poco==", stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        if not len(err) == 0:
            newest_version = EnvironmentUtils.parse_version(str(err))
        else:
            # maybe installed from source
            return
        if version < newest_version:
            ColorPrint.print_warning("New version of poco is available (%r). \n "
                                     "Please upgrade with: pip install -U poco" % newest_version)

    @staticmethod
    def parse_version(pip_content):
        if "(from versions: " in pip_content:
            first_line = pip_content.strip().splitlines()[0]
            versions = first_line.split(",")
            if len(versions[-1]) > 0:
                if ": " in versions[-1]:
                    return versions[-1][versions[-1].find(': ')+1:versions[-1].find(')')].strip()
                return versions[-1][0:versions[-1].find(')')].strip()
        return "0.0.0"

    @staticmethod
    def decode(text_string):
        if sys.version_info[0] == 3:
            return text_string.decode("utf-8")
        return text_string

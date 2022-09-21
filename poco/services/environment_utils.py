import os
import re
import sys
from packaging import version
from subprocess import Popen, PIPE
from poco.services.file_utils import FileUtils
from poco.services.state import StateHolder
from .console_logger import ColorPrint
from datetime import *


class EnvironmentUtils:

    @staticmethod
    def get_variable(key, default=None):
        return os.environ.get(key, default)

    @staticmethod
    def set_variable(key, value):
        os.environ[key] = value

    @staticmethod
    def set_poco_uid_and_gid():
        if os.name == "posix":
            EnvironmentUtils.set_variable("POCO_UID", str(os.getuid()))
            EnvironmentUtils.set_variable("POCO_GID", str(os.getgid()))

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
    def check_version(current_version, is_beta_tester, is_force_check):
        if (EnvironmentUtils.need_check() or is_force_check):
            # check pip
            p = Popen("pip install poco==", stdout=PIPE, stderr=PIPE, shell=True)
            out, err = p.communicate()
            if not len(err) == 0:
                newest_version = EnvironmentUtils.parse_version(str(err), is_beta_tester)
            else:
                # maybe installed from source
                return
            if version.parse(current_version) < version.parse(newest_version):
                ColorPrint.print_warning("New version of poco is available. \n "
                                        "Please upgrade with: pip install poco==" + newest_version)
            elif is_force_check:
                ColorPrint.print_warning("Poco is up to date")

    @staticmethod
    def parse_version(pip_content, is_beta_tester):
        """PIP response variations and expected versions:
        * '(from versions: 0.0.1,0.0.2)' - noDev: 0.0.2 isDev: 0.0.2
        * '(from versions: 0.0.1.dev1,0.0.2)' - noDev: 0.0.2 isDev: 0.0.2
        * '(from versions: 0.0.1,0.0.2.dev1)' - noDev: 0.0.1 isDev: 0.0.2.dev1

        not dev support : ^.*\\(from versions:.*(\\d+.\\d+.\\d+)[\\),].*$
        is dev support  : ^.*\\(from versions:.*(\\d+.\\d+.\\d+(\\.dev\\d+)?)[\\),].*$
        """
        version_expression = "^.*\\(from versions:.*(\\d+.\\d+.\\d+)[\\),].*$"
        if is_beta_tester:
            version_expression = "^.*\\(from versions:.*(\\d+.\\d+.\\d+(\\.dev\\d+)?)[\\),].*$"
        matches = re.findall(version_expression, pip_content)

        pre_ver = matches[0] if len(matches) > 0 else "0.0.0"
        return pre_ver[0] if type(pre_ver) is tuple else pre_ver

    @staticmethod
    def decode(text_string):
        if sys.version_info[0] == 3:
            return text_string.decode("utf-8")
        return text_string

    @staticmethod
    def need_check():
        directory = StateHolder.home_dir
        filename = "latest_update_check_date"
        latest_check_date = FileUtils.get_file_content(directory, filename)
        today = str(date.today())
        if (latest_check_date < today):
            FileUtils.write_to_file(directory, filename, today)
            return True
        return False

import os
import re
import sys
from packaging import version
from subprocess import Popen, PIPE, TimeoutExpired
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
        # Try commands in order; different kubectl versions support different flags
        EnvironmentUtils._check_command_with_fallback(
            ["kubectl version --client", "kubectl version"],
            "Kubernetes",
        )

    @staticmethod
    def check_helm():
        # Try commands in order; different helm versions support different flags
        EnvironmentUtils._check_command_with_fallback(
            ["helm version", "helm version --short", "helm --version"],
            "Helm",
        )

    @staticmethod
    def _check_command_with_fallback(commands, message_head):
        """Try each command until one returns 0. Makes checks work across kubectl/helm versions."""
        last_err = None
        for command in commands:
            p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
            out, err = p.communicate()
            if p.returncode == 0:
                text = (out or err or b"").decode("utf-8", errors="replace").strip()
                if text:
                    ColorPrint.print_with_lvl(message=message_head + "\n " + text, lvl=1)
                return
            last_err = (err or out or b"command failed").decode("utf-8", errors="replace").strip()
        ColorPrint.exit_after_print_messages(message=last_err or "command failed")

    @staticmethod
    def _check_command_ok(command, message_head):
        """Run command; require returncode 0. Many CLIs write version to stderr, so we accept either stdout or stderr."""
        p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        if p.returncode != 0:
            ColorPrint.exit_after_print_messages(message=(err or out or b"command failed").decode("utf-8", errors="replace").strip())
        text = (out or err or b"").decode("utf-8", errors="replace").strip()
        if text:
            ColorPrint.print_with_lvl(message=message_head + "\n " + text, lvl=1)

    @staticmethod
    def check_base(command, message_head):
        p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        if not len(err) == 0 or len(out) == 0:
            ColorPrint.exit_after_print_messages(message=str(err).strip())
        ColorPrint.print_with_lvl(message=message_head + "\n " + str(out).strip(), lvl=1)

    @staticmethod
    def check_version(current_version, is_beta_tester, is_force_check):
        if not (EnvironmentUtils.need_check() or is_force_check):
            return
        try:
            p = Popen("pip install poco==", stdout=PIPE, stderr=PIPE, shell=True)
            out, err = p.communicate(timeout=5)
        except TimeoutExpired:
            try:
                p.kill()
                p.wait()
            except Exception:
                pass
            return
        except Exception:
            return
        if not len(err) == 0:
            try:
                newest_version = EnvironmentUtils.parse_version(str(err), is_beta_tester)
            except Exception:
                return
            if version.parse(current_version) < version.parse(newest_version):
                ColorPrint.print_new_version(
                    "New version of poco is available.\n "
                    "Upgrade with: pip install poco==" + newest_version + "\n "
                    "or: pip install --upgrade poco"
                )
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

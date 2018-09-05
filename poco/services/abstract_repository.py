import os
import yaml
import sys
import platform
from .console_logger import ColorPrint
from .file_utils import FileUtils
from subprocess import Popen, PIPE
if sys.version_info[0] < 3:
    import urlparse
else:
    import urllib.parse as urlparse


class AbstractRepository(object):

    def __init__(self, target_dir):
        self.target_dir = target_dir

    def get_file(self, file):
        result = os.path.join(self.target_dir, file)
        return result

    def get_yaml_file(self, file, create=False):
        result = self.get_file(file)
        if not os.path.exists(result):
            if create:
                FileUtils.make_empty_file_with_empty_dict(directory=self.target_dir, file=file)
            else:
                return None
        try:
            with open(result) as stream:
                return yaml.load(stream)
        except yaml.YAMLError as exc:
            ColorPrint.exit_after_print_messages(
                message="Error: Wrong YAML format:\n " + str(exc), msg_type="warn")

    def write_yaml_file(self, file, content, overwrite=True, create=False):
        result = self.get_file(file)
        if create:
            if not os.path.exists(os.path.dirname(file)):
                os.makedirs(os.path.dirname(file))
        elif not os.path.exists(result):
            return
        if overwrite:
            with open(result, 'w') as stream:
                stream.write(content)
        else:
            with open(result, 'a') as stream:
                stream.write(content)

    def get_branches(self):
        return []

    def get_actual_branch(self):
        pass

    def set_branch(self, branch, force=False):
        ColorPrint.exit_after_print_messages(
            message="Error: branch is not supported in this repository. \n" + self.target_dir, msg_type="error")

    def print_branches(self):
        ColorPrint.print_with_lvl(message="Branch is not supported in this repository.", lvl=-1)

    def pull(self):
        pass

    def push(self):
        pass

    @staticmethod
    def check_remote(url):
        # TODO need a better solution
        o = urlparse.urlparse(url)
        host = o.netloc
        while "@" in host:
            host = host[host.find("@")+1:]
        while ":" in host:
            host = host[:host.find(":")]
        cmd = list()
        cmd.append("ping")
        if platform.system().lower().startswith("win"):
            cmd.append("-n")
            cmd.append("1")
            cmd.append("-w")
            cmd.append("1000")
        else:
            cmd.append("-c1")
            cmd.append("-t1")
        cmd.append(host)

        p = Popen(" ".join(cmd), stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()

        return len(err) == 0

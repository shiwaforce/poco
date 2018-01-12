import os
import shutil
import svn.remote
from .abstract_repository import AbstractRepository
from .console_logger import ColorPrint
from .file_utils import FileUtils


class SvnRepository(AbstractRepository):

    def __init__(self, target_dir, url):
        super(SvnRepository, self).__init__(target_dir)
        try:
            '''It's ugly, but the update method in LocalClient is not working'''
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, onerror=FileUtils.remove_readonly)

            self.repo = svn.remote.RemoteClient(url=url)
            self.repo.checkout(target_dir)
        except Exception as exc:
            ColorPrint.exit_after_print_messages(message=str(exc))

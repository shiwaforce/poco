import os
from .abstract_repository import AbstractRepository
from .console_logger import ColorPrint


class FileRepository(AbstractRepository):

    def __init__(self, target_dir):
        super(FileRepository, self).__init__(target_dir)
        if not os.path.exists(target_dir):
            ColorPrint.print_error(message="Base directory: %s not exist" % target_dir)
            ColorPrint.exit_after_print_messages(message="Please use project-catalog init for generate environment",
                                                 msg_type="warn")

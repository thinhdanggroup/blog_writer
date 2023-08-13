from datetime import datetime

from blog_writer.config.definitions import ROOT_DIR
from blog_writer.utils.file import write_file, read_file


class Storage:
    def __init__(self, subject: str, load_from_workspace: str = ""):
        if load_from_workspace != "":
            self.workspace = f"{ROOT_DIR}/.working_space/{load_from_workspace}"
        else:
            self.workspace = f"{ROOT_DIR}/.working_space/{self._get_working_folder(subject)}"

    def write(self, file_name: str, content: str):
        write_file(self.workspace + "/" + file_name, content)

    def read(self, file_name: str) -> str:
        return read_file(self.workspace + "/" + file_name)

    def _get_working_folder(self, name: str) -> str:
        dt = datetime.now()
        unique_time = dt.strftime('%y%m%d%H%M%S')
        return unique_time + "_" + name.strip().replace(" ", "_").lower()[0:20]

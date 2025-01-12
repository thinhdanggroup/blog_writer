from typing import List

from datetime import datetime
import re
from blog_writer.agents.title_generator import TitleGenerator
from blog_writer.config.config import ModelConfig, new_model_config

from blog_writer.config.definitions import ROOT_DIR, LLMType, OpenRouterModel
from blog_writer.utils.file import write_file, read_file, list_files


class Storage:
    def __init__(
        self,
        subject: str,
        load_from_workspace: str = "",
        model_config: ModelConfig = None,
    ):
        if model_config is not None:
            self.title_generator = TitleGenerator(
                model_config=model_config,
            )
        self.working_name = load_from_workspace
        if load_from_workspace != "":
            self.workspace = f"{ROOT_DIR}/.working_space/{load_from_workspace}"
        else:
            name = self._get_working_folder(subject)
            self.workspace = f"{ROOT_DIR}/.working_space/{name}"
            self.working_name = name

    def write(self, file_name: str, content: str):
        write_file(self.workspace + "/" + file_name, content)

    def read(self, file_name: str) -> str:
        return read_file(self.workspace + "/" + file_name)

    def list(self, sub_folder: str) -> List[str]:
        full_path, relative = list_files(f"{self.workspace}/{sub_folder}")
        return relative

    def _get_working_folder(self, name: str) -> str:
        generated_name = self.title_generator.run(name).description

        dt = datetime.now()
        unique_time = dt.strftime("%y%m%d%H%M%S")
        name = re.sub(
            "[^a-zA-Z0-9-_]", "-", generated_name.replace(" ", "-").lower()[0:60]
        )

        self.generated_name = name
        return unique_time + "_" + name

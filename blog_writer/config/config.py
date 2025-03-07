"""Configuration class to store the state of bools for different scripts access."""

import os
from typing import Any

from dotenv import load_dotenv

from blog_writer.config.definitions import ROOT_DIR, MODEL_GPT_35, LLMType


def get_bool(raw: Any, default: bool = False) -> bool:
    return str(raw).lower() == "true" if raw is not None else default


class ModelConfig:
    def __init__(self, llm_type: str = "azure"):
        self.llm_type = llm_type
        prefix = llm_type.upper() + "_"
        self.deployment = os.getenv(prefix + "MODEL_CONFIG_DEPLOYMENT", MODEL_GPT_35)
        self.version = os.getenv(prefix + "MODEL_CONFIG_VERSION")
        self.base = os.getenv(prefix + "MODEL_CONFIG_BASE")
        self.username = os.getenv(prefix + "MODEL_CONFIG_USERNAME", "")
        self._key1 = os.getenv(prefix + "MODEL_CONFIG_KEY")
        self._key2 = os.getenv(prefix + "MODEL_CONFIG_KEY2", self._key1)
        self._keys = [self._key1, self._key2]
        self._current_index = 0

    @property
    def key(self):
        current_key = self._keys[self._current_index]
        self._current_index = (self._current_index + 1) % len(self._keys)
        return current_key

    def model_dump(self):
        return {
            "llm_type": self.llm_type,
            "deployment": self.deployment,
            "version": self.version,
            "base": self.base,
            "username": self.username,
        }


def new_model_config(deployment: str, llm_type: str = LLMType.GEMINI) -> ModelConfig:
    cfg = ModelConfig(llm_type=llm_type)
    cfg.deployment = deployment
    return cfg


class WebSearchConfig:
    def __init__(self):
        self.search_engine = os.getenv("SEARCH_ENGINE", "ddg")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID", "")
        self.num_results = int(os.getenv("NUM_RESULTS", "5"))


class WebExtractorConfig:
    def __init__(self):
        self.with_summary = get_bool(os.getenv("WITH_SUMMARY", "true"))
        self.temperature = float(os.getenv("WEB_EXTRACTOR_TEMPERATURE", "0.7"))
        self.use_cache = get_bool(os.getenv("WEB_USE_CACHE", "false"))


class GenerateBlogConfig:
    def __init__(self):
        self.writer_generate_image_per_step = get_bool(
            os.getenv("WRITER_GENERATE_IMAGE_PER_STEP", "true")
        )
        self.writer_visualize_per_step = get_bool(
            os.getenv("WRITER_VISUALIZE_PER_STEP", "true")
        )
        self.writer_generate_image = get_bool(
            os.getenv("WRITER_GENERATE_IMAGE", "false")
        )
        self.add_references = get_bool(os.getenv("ADD_REFERENCES", "true"))
        self.crawl_reference_urls = get_bool(os.getenv("CRAWL_REFERENCE_URLS", "false"))
        self.add_file_references = get_bool(os.getenv("ADD_FILE_REFERENCES", "false"))


class Config:
    def __init__(self):
        self.model_config_gemini = ModelConfig(llm_type=LLMType.GEMINI)
        self.model_config_or = ModelConfig(llm_type=LLMType.OPEN_ROUTER)
        self.model_config_ollama = ModelConfig(llm_type=LLMType.OLLAMA)
        self.model_config_hf_chat = ModelConfig(llm_type=LLMType.HF_CHAT)
        self.model_config_ts_chat = ModelConfig(llm_type=LLMType.TS_CHAT)
        self.web_extractor = WebExtractorConfig()
        self.web_search = WebSearchConfig()
        self.generate_blog = GenerateBlogConfig()


def load_config() -> Config:
    load_dotenv(dotenv_path=f"{ROOT_DIR}/.env.template", verbose=True)
    load_dotenv(dotenv_path=f"{ROOT_DIR}/.env", override=True, verbose=True)
    return Config()

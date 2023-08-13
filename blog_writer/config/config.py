"""Configuration class to store the state of bools for different scripts access."""
import os
from typing import Any

from dotenv import load_dotenv

from blog_writer.config.definitions import ROOT_DIR


def get_bool(raw: Any, default: bool = False) -> bool:
    return str(raw).lower() == "true" if raw is not None else default


class ModelConfig:
    def __init__(self):
        self.deployment = os.getenv("MODEL_CONFIG_DEPLOYMENT")
        self.version = os.getenv("MODEL_CONFIG_VERSION")
        self.base = os.getenv("MODEL_CONFIG_BASE")
        self.key = os.getenv("MODEL_CONFIG_KEY")


def new_model_config(deployment) -> ModelConfig:
    cfg = ModelConfig()
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


class Config:
    def __init__(self):
        self.model_config = ModelConfig()
        self.web_extractor = WebExtractorConfig()
        self.web_search = WebSearchConfig()


def load_config() -> Config:
    load_dotenv(dotenv_path=f"{ROOT_DIR}/.env.template", verbose=True)
    load_dotenv(dotenv_path=f"{ROOT_DIR}/.env", override=True, verbose=True)
    return Config()

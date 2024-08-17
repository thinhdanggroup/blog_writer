from enum import Enum, StrEnum
import os

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "../.."))
MODEL_AZURE_CHATGPT = "azure-chatgpt"

# MODEL_NAME = "gpt-4-32k-0613"
# MODEL_NAME = "gpt4-32k"
# MODEL_NAME = "gpt-4-1106-preview"
MODEL_GPT_35 = "gpt35-turbo-16k"
MODEL_NAME = "gemini-pro"
MODEL_NAME_GEMINI_PRO_15 = "gemini-1.5-pro-latest"


class LLMType(StrEnum):
    AZURE = "azure"
    GEMINI = "gemini"
    OPEN_ROUTER = "open_router"
    BING_CHAT = "bing_chat"
    OLLAMA = "ollama"
    HF_CHAT = "hf_chat"
    TS_CHAT = "ts_chat"


# Models: https://openrouter.ai/docs/models
class OpenRouterModel(Enum):
    OR_NOUSRESEARCH_NOUS_CAPYBARA_7B_FREE = ("nousresearch/nous-capybara-7b:free", 4096)
    OR_MISTRALAI_MISTRAL_7B_INSTRUCT_FREE = (
        "mistralai/mistral-7b-instruct:free",
        32768,
    )
    OR_GRYPHE_MYTHOMIST_7B_FREE = ("gryphe/mythomist-7b:free", 32768)
    OR_UNDI95_TOPPY_M_7B_FREE = ("undi95/toppy-m-7b:free", 4096)
    OR_GOOGLE_GEMMA_7B_IT_FREE = ("google/gemma-7b-it:free", 8000)
    OR_OPENROUTER_CINEMATIKA_7B_FREE = ("openrouter/cinematika-7b:free", 8000)
    OR_HUGGINGFACEH4_ZEPHYR_7B_BETA_FREE = ("huggingfaceh4/zephyr-7b-beta:free", 4096)
    OR_OPENCHAT_OPENCHAT_7B_FREE = ("openchat/openchat-7b:free", 8192)
    PHI_3_MINI = ("microsoft/phi-3-mini-128k-instruct:free", 128000)
    PHI_3_MEDIUM = ("microsoft/phi-3-medium-128k-instruct:free", 128000)
    LLAMA_3_8B = ("meta-llama/llama-3-8b-instruct:free", 8192)
    NOUS_RESEARCH_CAPYBARA_7B = ("nousresearch/nous-capybara-7b:free", 4096)


class OllamaModel(Enum):
    MISTRAL = "mistral"
    LLAMA3 = "llama3"
    GEMMA = "gemma"


class HFModel(Enum):
    CO_HERE_FOR_AI = "CohereForAI/c4ai-command-r-plus"
    ZEPHYR = "HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1"
    MISTRAL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    GEMMA = "google/gemma-1.1-7b-it"
    MISTRAL_7B = "mistralai/Mistral-7B-Instruct-v0.2"
    PHI_3_MINI = "microsoft/Phi-3-mini-4k-instruct"
    LLAMA3 = "meta-llama/Meta-Llama-3-70B-Instruct"


class TSModel(Enum):
    GPT_4_TURBO_PREVIEW = "gpt-4-turbo-preview"
    GPT_4O = "gpt-4o"
    GPT_35_TURBO = "gpt-3.5-turbo"

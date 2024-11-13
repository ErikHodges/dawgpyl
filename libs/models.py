from dataclasses import dataclass

from configs.models import MODELS
from configs.apis import APIS
from langchain_core.language_models.base import BaseLanguageModel
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import SecretStr


@dataclass(slots=False)
class Model:
    """Class for LLM and Embedder clients"""

    type: str | None
    api: str | None
    api_key: SecretStr | str | None
    size: str | None
    name: str | None
    client: BaseLanguageModel | None

    def __init__(self, model_spec: dict = {"type": "llm", "api": "openai", "size": "default"}):
        self.type = model_spec["type"]
        self.api = model_spec["api"]
        self.size = model_spec["size"]
        self.api_key = APIS[self.api]["key"]
        self.name = MODELS[self.api][self.type][self.size]
        self.client = BaseLanguageModel

    def instantiate_client(self, agent_config):
        if self.api == "openai":

            self.client = ChatOpenAI(
                model=self.name,
                openai_api_key=self.api_key.get_secret_value(),
                max_tokens=agent_config.max_tokens,
                temperature=agent_config.temperature,
                # top_p=agent_config.top_p,
                max_retries=agent_config.max_retries,
                timeout=agent_config.timeout,
                response_format=agent_config.response_format,
            )
        elif self.api == "nvidia":
            self.client = ChatNVIDIA(
                model=self.name,
                api_key=self.api_key.get_secret_value(),
                temperature=agent_config.temperature,
                # top_p=agent_config.top_p,
                seed=agent_config.seed,
                max_tokens=agent_config.max_tokens,
            )
        elif self.api == "anthropic":
            self.client = ChatAnthropic(
                model=self.name,
                api_key=self.api_key.get_secret_value(),
                temperature=agent_config.temperature,
                # top_p=agent_config.top_p,
                seed=agent_config.seed,
                max_tokens=agent_config.max_tokens,
            )

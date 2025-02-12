""" This module contains the Model class, used to define the model endpoints that are assigned to agents."""

from dataclasses import dataclass
from pydantic import BaseModel, SecretStr
from typing import Optional, Union, Dict, List, Any
from pydantic import BaseModel, Field


from langchain_core.language_models import BaseLanguageModel

from configs.apis import APIS

DEFAULT_MODELS = {
    "llm": {"api": "openai"},
    "embedding": {"api": "nvidia"},
}


class ModelConfig(BaseModel):
    """Class for model configuration"""
    args: Optional[Dict[str, Any]] = Field(default_generator=None,init=True,description="")
    kwargs: Optional[Dict[str, Any]] = Field(default=None,init=True,description="")
    type: Optional[str] = Field(default="llm",init=True,description="")
    size: Optional[str] = Field(default="default",init=True,description="")
    api: Optional[str] = Field(default=DEFAULT_MODELS["llm"]["api"],init=True,description="")
    api_key: Optional[Union[SecretStr,str]] = Field(default=None,init=True,description="")

    def __init__(self, **kwargs): 
        self.type = kwargs.get("type", "llm")
        self.size = kwargs.get("size", DEFAULT_MODELS["llm"]["size"])
        self.api = kwargs.get("size", DEFAULT_MODELS["llm"]["api"])
        self.api_key = APIS[self.api]["key"].get_secret_value()


# @dataclass(slots=False)
class Model(BaseModel):
    """Class for LLM and Embedder clients"""

    config: ModelConfig = ModelConfig()
    name: str | None
    client: BaseLanguageModel | None

    def __init__(self, model_config: ModelConfig = ModelConfig()):
        self.config = model_config
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


MODELS = {
    "openai": {
        "key": APIS["openai"]["key"].get_secret_value(),
        "llm": {
            "names": [
                "gpt-3.5-turbo",
                "gpt-4-turbo",
                "gpt-4o",
                "gpt-4o-realtime-preview",
                "o1",
                "o1-mini",
                # "o3",
                "o3-mini",
            ],
            "default": "o3-mini",
            "small": "o3-mini",
            "medium": "o3-mini",
            "large": "o1",
        },
        "embedder": {
            "names": [
                "text-embedding-3-small",
                "text-embedding-3-large",
            ],
            "default": "text-embedding-3-large",
            "small": "text-embedding-3-small",
            "medium": "text-embedding-3-large",
            "large": "text-embedding-3-large",
        },
    },
    "nvidia": {
        "key": APIS["nvidia"]["key"].get_secret_value(),
        "llm": {
            "names": [
                "mistralai/mixtral-8x7b-instruct-v0.1",
                "mistralai/mixtral-8x22b-instruct-v0.1",
                "mistralai/mistral-large",
                "meta/llama3-70b-instruct",
            ],
            "default": "mistralai/mistral-large",
            "small": "mistralai/mixtral-8x7b-instruct-v0.1",
            "medium": "mistralai/mixtral-8x22b-instruct-v0.1",
            "large": "mistralai/mistral-large",
            "meta": "meta/llama3-70b-instruct",
        },
        "embedder": {
            "names": ["nvidia/NV-Embed-QA-4"],
            "default": "nvidia/NV-Embed-QA-4",
            "small": "nvidia/NV-Embed-QA-4",
            "medium": "nvidia/NV-Embed-QA-4",
            "large": "nvidia/NV-Embed-QA-4",
        },
    },
    "anthropic": {
        "key": APIS["nvidia"]["key"].get_secret_value(),
        "llm": {
            "default": "claude-3-5-sonnet-20240620",
            "small": "claude-3-opus-20240229",
            "medium": "claude-3-opus-20240229",
            "large": "claude-3-5-sonnet-20240620",
        },
    },
}

from pydantic import SecretStr

# TODO: Remove api keys from the models file
MODELS = {
    "openai": {
        "llm": {
            "names": ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o", "o1-mini", "o1-preview"],
            "default": "o1-preview",
            "small": "o1-mini",
            "medium": "gpt-4o",
            "large": "o1-preview",
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
        "default": "claude-3-5-sonnet-20240620",
        "small": "claude-3-opus-20240229",
        "medium": "claude-3-opus-20240229",
        "large": "claude-3-5-sonnet-20240620",
    },
}

# DEFAULT_LLM = {
#     "api": "nvidia",  # MODELS[api]['key']
#     "size": "small",  # ['models']['llms'][size]
# }
DEFAULT_LLM = {
    "api": "openai",  # MODELS[api]['key']
    "size": "default",  # ['models']['llms'][size]
}
DEFAULT_EMBEDDER = {
    "api": "nvidia",  # MODELS[api]['key']
    "size": "default",  # ['models']['embedders'][size]
}

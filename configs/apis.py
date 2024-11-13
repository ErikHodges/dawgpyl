from pydantic import SecretStr

# To retrieve the value, use: APIS[api_name]["key"].get_secret_value()
APIS = {
    "anthropic": {
        "key": SecretStr(""),
        "user": "",
    },
    "mistral": {
        "key": SecretStr(""),
        "user": "",
    },
    "openai": {
        "key": SecretStr(""),
    },
    "huggingface": {
        "key": SecretStr(""),
    },
    "nvidia": {
        "key": SecretStr(""),
        "id": SecretStr(""),
        "name": "",
        "expiration": "",
    },
    "ncbi": {
        "key": SecretStr(""),
        "user": "",
    },
    "tavily": {
        "key": SecretStr(""),
    },
    "langsmith": {
        "key": SecretStr(""),
    },
    "serper": {"key": SecretStr("")},
}

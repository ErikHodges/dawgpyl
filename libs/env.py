"""This module contains the environmental setup script for AI Agent development."""

import os
import platform
import sys
import warnings

sys.dont_write_bytecode = True
DEFAULT_SEED = 12354

from configs.apis import APIS

# This warning is filtered from langgraph
warnings.filterwarnings("ignore", message="WARNING! response_format is not")

print(os.path.abspath(os.getcwd()))

# Using system() method to execute shell commands
if platform.system() == "Linux":
    REPO_ROOT = os.path.abspath("/home/orangepi/Documents/Code/ml_apps")
else:
    REPO_ROOT = os.path.abspath("/Code/dawgpyl")

os.chdir(REPO_ROOT)
CODE_ROOT = os.path.join(REPO_ROOT, "code")
if CODE_ROOT not in sys.path:
    sys.path.append(CODE_ROOT)



os.environ["OPENAI_API_KEY"] = APIS["openai"]["key"].get_secret_value()
os.environ["LANGCHAIN_API_KEY"] = APIS["langsmith"]["key"].get_secret_value()
os.environ["TAVILY_API_KEY"] = APIS["tavily"]["key"].get_secret_value()
os.environ["HF_API_KEY"] = APIS["huggingface"]["key"].get_secret_value()

# Optional, add tracing in LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent COPILOT"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["HF_HOME"] = os.path.join(REPO_ROOT, "data", "models")

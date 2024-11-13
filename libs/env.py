"""This module contains utility functions for general AI model development."""

import os
import platform
import sys

sys.dont_write_bytecode = True

import datetime as dt
import json
import os
import re
import subprocess
import warnings
from dataclasses import dataclass
from pprint import pprint
from typing import Annotated, Sequence, TypedDict

from uuid import uuid4

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from termcolor import colored
from pydantic import SecretStr

pd.set_option("mode.copy_on_write", True)

# This warning is filtered from langgraph
warnings.filterwarnings("ignore", message="WARNING! response_format is not")

print(os.getcwd())
# os.chdir("..")
# print(os.getcwd())

if platform.system() == "Linux":
    REPO_ROOT = "/home/orangepi/Documents/Code/ml_apps/"
else:
    REPO_ROOT = "/Code/dawgpyl"

os.chdir(REPO_ROOT)
CODE_ROOT = os.path.join(REPO_ROOT, "/code")
if CODE_ROOT not in sys.path:
    sys.path.append(CODE_ROOT)


from libs.base import *

import langchain
from configs.apis import *
from configs.agents import *
from configs.core import *
from configs.models import *
from configs.projects import *
from configs.prompts import *
from configs.tasks import *
from configs.teams import *
from configs.tools import *
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import OpenAI
from langgraph.graph import END, StateGraph
from libs.agent_tools import *
from libs.agents import *

from libs.common import *
from libs.file_conversions import *
from libs.graphs import *
from libs.io import *
from libs.models import *
from libs.projects import *
from libs.tasks import *
from libs.teams import *
from openai import OpenAI

# Using system() method to
# execute shell commands

os.environ["OPENAI_API_KEY"] = APIS["openai"]["key"].get_secret_value()
os.environ["LANGCHAIN_API_KEY"] = APIS["langsmith"]["key"].get_secret_value()
os.environ["TAVILY_API_KEY"] = APIS["tavily"]["key"].get_secret_value()
os.environ["HF_API_KEY"] = APIS["huggingface"]["key"].get_secret_value()

# Optional, add tracing in LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent COPILOT"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["HF_HOME"] = Directories().models

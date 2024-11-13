# Library containing tools and functions that agents should have access to
import datetime as dt
import json
import os
from typing import TypedDict

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

from configs.apis import APIS
from libs.common import print_dict, eprint

pd.set_option("mode.copy_on_write", True)


def search_web(search_str: str):
    return print(f"Searching for: {search_str}")


def scrape_website(url):
    try:
        # Fetch the web page content
        response = requests.get(url)
        response.raise_for_status()
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract the text from the HTML
        text = " ".join([p.get_text() for p in soup.find_all("p")])
        return text
    except Exception as e:
        return str(e)


def describe_tool(tool):
    tool_description = tool.__doc__
    return tool_description


# class Prompts(TypedDict):
#     system:str
#     default:str
#     user:str

# prompts = Prompts(
#     **{
#     "system":"",
#     "default":",
#     "user":"",
#     }
# )

# print(prompts.user)
# print(prompts.system)

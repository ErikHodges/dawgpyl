## Common functions that are used across projects and classes

import base64
import inspect
import json
import os
import re
import sqlite3
from datetime import datetime as dt
import urllib.error
import urllib.parse
import urllib.request
from pprint import pprint
from random import Random

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from markdownify import markdownify
from IPython.display import Markdown
from random_word import RandomWords
from termcolor import colored
from openai import OpenAI
from configs.apis import APIS

color_names = [
    "green",
    "light_magenta",
    "blue",
    "yellow",
    "cyan",
    "light_green",
    "magenta",
    "white",
    "light_red",
    "light_blue",
    "red",
    "light_grey",
    "dark_grey",
    "light_yellow",
    "light_cyan",
]


def get_class(variable: object) -> str:
    """Return the class of a variable as a string.

    Args:
        variable (object): The variable whose class is to be retrieved.

    Returns:
        str: The base class of the variable as a string.
    """
    base_class = str(type(variable)).replace("'>", "").split(".")[-1]
    return base_class


def get_varname(variable: object) -> str:
    """Return the name of a variable as a string.

    Args:
        variable (object): The variable whose name is to be retrieved.

    Returns:
        str: The name of the variable.
    """
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is variable][0]


def describe_variable(variable: object) -> None:
    """Describe a variable by printing its name and length.

    Args:
        variable (object): The variable to be described.

    Returns:
        None
    """
    varname = get_varname(variable)
    print(f"{len(varname) = }")
    print(f"{varname = }")
    return None


def eprint(printable: object, width: int = 80) -> None:
    """Pretty print a given object with no sorting,

    Args:
        printable (object): The object to be pretty printed.

    Returns:
        None
    """
    return pprint(printable, sort_dicts=False, width=width)


def parse_agent_response(full_response: object, expected_response_type: str) -> str:
    """Parse the agent response based on the expected response type.

    Args:
        full_response (object): The full response object.
        expected_response_type (str): The expected type of the response (e.g., "json_object").

    Returns:
        str: The parsed message from the response.
    """
    if expected_response_type == "json_object":
        try:
            response_content = json.loads(full_response.content)
            if response_content.get("response"):
                message = response_content.get("response")
            elif response_content.get("type") == "string":
                message = response_content.get("properties").get("response").get("description")
            elif response_content.get("type") == "object":
                message = response_content.get("properties").get("response").get("description")
            else:
                message = full_response.content
        except Exception as e:
            message = full_response.content
    else:
        message = full_response.content
    return message


def generate_random_name() -> str:
    """Generate a random name using the RandomWords library.

    Returns:
        str: A randomly generated name.
    """
    random_name = RandomWords().get_random_word()
    return random_name


def print_heading(title_text: str, color: str = "cyan") -> None:
    """Print a heading with a title enclosed in dashes.

    Args:
        title_text (str): The title text to be printed.
        color (str, optional): The color of the heading. Defaults to "cyan".

    Returns:
        None
    """
    title_length = len(title_text)
    title_bar = "----" + ("-" * title_length) + "----"
    print(colored(title_bar, color, attrs=["bold"]))
    print(colored(f"    {title_text}", color, attrs=["bold"]))
    print(colored(title_bar, color, attrs=["bold"]))
    return None


def replace_placeholders(text: str, variables: dict) -> str:
    """Replace placeholders in the text with actual variable values.

    Args:
        text (str): The text containing placeholders.
        variables (dict): A dictionary of variable names and their values.

    Returns:
        str: The text with placeholders replaced with variable values.

    Raises:
        ValueError: If a placeholder does not have a corresponding value in the dictionary.
    """
    pattern = re.compile(r"\{(\w+)\}")
    matches = pattern.findall(text)

    for match in matches:
        if match in variables:
            text = text.replace("{" + match + "}", str(variables[match]))
        else:
            raise ValueError(f"No replacement found for placeholder {{{match}}}")

    return text


def replace_in_dict(input_dict: dict, variables: dict) -> dict:
    """Recursively replace placeholders in the dictionary values with variable values.

    Args:
        input_dict (dict): The input dictionary containing placeholders.
        variables (dict): A dictionary of variable names and their values.

    Returns:
        dict: The input dictionary with placeholders replaced.
    """
    for key, value in input_dict.items():
        if isinstance(value, str):
            input_dict[key] = replace_placeholders(value, variables)
        elif isinstance(value, dict):
            input_dict[key] = replace_in_dict(value, variables)
        elif isinstance(value, list):
            input_dict[key] = [
                replace_placeholders(item, variables) if isinstance(item, str) else item
                for item in value
            ]

    return input_dict


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Get the cosine similarity between two vectors.

    Args:
        v1 (np.ndarray): The first vector.
        v2 (np.ndarray): The second vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def print_dict(dict2print: dict, color: str = "cyan") -> None:
    """Print a dictionary with colored keys and values.

    Args:
        dict2print (dict): The dictionary to be printed.
        color (str, optional): The color of the keys. Defaults to "cyan".

    Returns:
        None
    """
    if not ((hasattr(dict2print, "items")) and (callable(dict2print.items))):
        dict2print = dict2print.__dict__

    for k, v in dict2print.items():
        k = k + ":"
        printkey = colored(f"{k:<10}", color=color, attrs=["bold"])
        printval = colored(f"{v}", color=color)

        print(printkey, printval)


def map_member_colors(member_names: list, color_names: list) -> dict:
    """Map member names to colors.

    Args:
        member_names (list): A list of member names.
        color_names (list): A list of color names.

    Returns:
        dict: A dictionary mapping member names to colors.
    """
    member_colors = {}
    for idx, member_name in enumerate(member_names):
        member_colors[member_name] = color_names[idx]
    return member_colors

def print_md(markdown_str:str):
    return Markdown(markdown_str)


def query_database(database: sqlite3.Connection, query: str) -> None:
    """Execute a query on the SQLite database.

    Args:
        database (sqlite3.Connection): The SQLite database connection.
        query (str): The SQL query to be executed.

    Returns:
        None
    """
    cursor = database.cursor()
    try:
        cursor.execute(query)
        database.commit()
        print("Query executed successfully")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")




# from libs.io import read_file,write_file
# from libs.base import Timestamp

# def log_response(response,model_name,):
#     filename = Timestamp().filestamp
#     if dt.now().isoformat()[:11]==filename[:11]:
#         try:
#             filename = [f for f in os.listdir(dirs.logs) if f.startswith(f"{filename[:11]}")][0]
#         except:
#             pass

#     filepath = os.path.join(dirs.logs, filename+'.py')
#     model_artifact = {
#         "run_datetime": Timestamp().iso,
#         "model_config": model_name,
#         "prompt_system": prompt_system,
#         "prompt_user": prompt_user,
#         "response": response.choices[0].message.content,
#         "usage":response.usage.__dict__,
#         "full_response": response,
#     }
#     log_text = f"log = [{model_artifact}]"
#     write_file(log_text, filepath)


def chat(
    model_name: str = "gpt-4o",
    prompt_system: str = "You are a helpful assistant.",
    prompt_user: str = "Tell me a story about a fire department run by bunnies.",
    max_tokens=None,
):
    try:
        response = OpenAI(
            api_key=APIS.get("openai").get("key").get_secret_value()
        ).chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user},
            ],
            max_tokens=max_tokens,
        )

        return response
    except Exception as e:
        return str(e)


def log_response(response, chat_config, dirs):
    from libs.base import Timestamp
    from libs.io import read_file, write_file

    log_exists = False

    log_prefix = "log_"
    filename = log_prefix + Timestamp().date
    len_datestr = 11

    if (
        dt.now().isoformat()[:len_datestr]
        == filename[len(log_prefix) : len(log_prefix) + len_datestr]
    ):
        try:
            filename = [
                f for f in os.listdir(dirs.logs) if f.startswith(f"{filename[:len_datestr]}")
            ][0]
            log_exists = True
        except:
            pass

    filepath = os.path.join(dirs.logs, filename + ".joblib")
    model_artifact = {
        "run_datetime": Timestamp().iso,
        "model_config": chat_config["model_name"],
        "prompt_system": chat_config["prompt_system"],
        "prompt_user": chat_config["prompt_user"],
        "response": response.choices[0].message.content,
        "usage": response.usage.__dict__,
        "full_response": response,
    }
    if log_exists:
        log = read_file(filepath)
        # log_text = read_file(log_file_path)
        # log = eval(log_text.replace("log = ", ""))
        log.append(model_artifact)
    else:
        log = [model_artifact]
    write_file(log, filepath)
    return print(f"Response logged to: {filepath}")

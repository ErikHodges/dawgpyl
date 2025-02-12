## Common functions that are used across projects and classes

import inspect
import json
import os
import re
import sqlite3
from datetime import datetime as dt

import numpy as np
from IPython.display import display
from openai import OpenAI
from random_word import RandomWords

from configs.apis import APIS


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
        messages = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        if "o1-preview" in model_name:
            for msg_idx, msg in enumerate(messages):
                if msg["role"] == "system":
                    messages[msg_idx]["role"] = "user"

        response = OpenAI(
            api_key=APIS.get("openai").get("key").get_secret_value()
        ).chat.completions.create(
            model=model_name,
            messages=messages,
            max_completion_tokens=max_tokens,
        )

        return response
    except Exception as e:
        return str(e)


def log_response(response, chat_config, dirs):
    from dawgpyl.libs.base import Timestamp
    from libs.utils.io import read_file, write_file

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


def print_log_entry(log, entry_num=-1):
    log_entry = log[entry_num]
    print_heading("LOG ENTRY", "blue")
    print("run_datetime: ", log_entry["run_datetime"])
    print("model_config: ", log_entry["model_config"])
    print("prompt_tokens: ", log_entry["usage"]["prompt_tokens"])
    print("completion_tokens: ", log_entry["usage"]["completion_tokens"])
    print_heading("prompt_user")
    print(log_entry["prompt_user"])
    print_heading("prompt_system")
    print(log_entry["prompt_system"])
    print_heading("response")
    display(print_md(log_entry["response"]))
    print_heading("FULL LOG ENTRY")
    eprint(log_entry)

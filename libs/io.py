## Common functions that are used across projects and classes

import base64
import inspect
import json
import os
import re
# import h5py
import urllib.error
import urllib.parse
import urllib.request

from libs.common import get_varname
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from markdownify import markdownify
import sqlite3
import joblib


def check_exists(filepath: str) -> bool:
    """Checks if a file exists at the specified filepath.

    Args:
        filepath (str): The path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.exists(filepath)


def print_io_status(filepath: str, action: str, status: str, **kwargs) -> None:  # type: ignore
    """Prints the status of an I/O operation.

    Args:
        filepath (str): The path to the file being read or written.
        action (str): The action being performed (e.g., READ, WRITE).
        status (str): The status of the action (e.g., SUCCESS, FAIL).
        error (Exception, optional): The error encountered, if any. Defaults to None.
    """
    error = kwargs.get("error", None)
    if error:
        print(f"{action} {status}:\n{filepath}\nError: {error}")
    else:
        print(f"{action} {status}:\n{filepath}")


### CSV
def read_csv(filepath: str) -> pd.DataFrame | None:
    """Reads a CSV file and returns its contents as a DataFrame.

    This function attempts to read a CSV file from the specified filepath. If
    successful, it logs a "SUCCESS" status and returns the contents of the file
    as a DataFrame. If an error occurs, it logs a "FAIL" status.

    Args:
        filepath (str): The path to the CSV file to be read.

    Returns:
        pd.DataFrame: The contents of the CSV file if read successfully,
        otherwise None.

    Raises:
        Exception: If any error occurs during reading the CSV file.
    """
    action = "READ"
    try:
        contents = pd.read_csv(filepath)
        print_io_status(filepath, action, status="SUCCESS")
        return contents
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)
        return None


def write_csv(content: pd.DataFrame, filepath: str) -> None:
    """Writes the given DataFrame to a CSV file.

    Args:
        content (pd.DataFrame): The DataFrame to write to the CSV file.
        filepath (str): The path to the CSV file to be written.
    """
    action = "WRITE"
    if check_exists(filepath):
        action = "OVERWRITE"
    try:
        content.to_csv(filepath, header=True, index=False)
        print_io_status(filepath, action, status="SUCCESS")
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)


### XLSX
def read_xlsx(filepath: str) -> pd.DataFrame | None:
    """Reads an Excel (XLSX) file and returns its contents as a DataFrame.

    Args:
        filepath (str): The path to the XLSX file to be read.

    Returns:
        pd.DataFrame: The contents of the XLSX file if read successfully,
        otherwise None.
    """
    action = "READ"
    try:
        contents = pd.read_excel(filepath)
        print_io_status(filepath, action, status="SUCCESS")
        return contents
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)
        return None


### PARQUET
def read_parquet(filepath: str) -> pd.DataFrame | None:
    """Reads a Parquet file and returns its contents as a DataFrame.

    Args:
        filepath (str): The path to the Parquet file to be read.

    Returns:
        pd.DataFrame: The contents of the Parquet file if read successfully,
        otherwise None.
    """
    action = "READ"
    try:
        contents = pq.read_table(filepath).to_pandas()
        print_io_status(filepath, action, status="SUCCESS")
        return contents
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)
        return None


def write_parquet(content: pd.DataFrame | pa.Table, filepath: str) -> None:
    """Writes the given DataFrame or PyArrow Table to a Parquet file.

    Args:
        content (pd.DataFrame or pa.Table): The content to write to the Parquet file.
        filepath (str): The path to the Parquet file to be written.
    """
    action = "WRITE"
    if check_exists(filepath):
        action = "OVERWRITE"
    try:
        if isinstance(content, pd.DataFrame):
            df_pa = pa.Table.from_pandas(content)
            pq.write_table(df_pa, filepath)
        elif isinstance(content, pa.Table):
            pq.write_table(content, filepath)
        print_io_status(filepath, action, status="SUCCESS")
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)


### JSON
def read_json(filepath: str) -> dict | None:
    """Reads a JSON file and returns its contents as a dictionary.

    Args:
        filepath (str): The path to the JSON file to be read.

    Returns:
        dict: The contents of the JSON file if read successfully,
        otherwise None.
    """
    action = "READ"
    try:
        with open(filepath, "r", encoding="utf-8") as file_in:
            content = json.load(file_in)
            print_io_status(filepath, action, status="SUCCESS")
        return content
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)
        return None


def write_json(content: dict, filepath: str) -> None:
    """Writes the given dictionary to a JSON file.

    Args:
        content (dict): The content to write to the JSON file.
        filepath (str): The path to the JSON file to be written.
    """
    action = "WRITE"
    if check_exists(filepath):
        action = "OVERWRITE"
    try:
        if (isinstance(content, dict)) and (".json" in os.path.basename(filepath)):
            content = json.dumps(content)
        with open(filepath, "w+", encoding="utf-8") as outfile:
            json.dump(content, outfile, indent=4)
        print_io_status(filepath, action, status="SUCCESS")
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)


### JOBLIB
def read_joblib(filepath: str) -> str | None:
    """Reads a text file and returns its contents as a string.

    Args:
        filepath (str): The path to the text file to be read.

    Returns:
        str: The contents of the text file if read successfully,
        otherwise None.
    """
    action = "READ"
    try:
        with open(filepath, "rb") as file_in:
            content = joblib.load(file_in)
        print_io_status(filepath, action, status="SUCCESS")
        return content
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)
        return None


def write_joblib(content: dict, filepath: str) -> str | None:
    """Reads a text file and returns its contents as a string.

    Args:
        filepath (str): The path to the text file to be read.

    Returns:
        str: The contents of the text file if read successfully,
        otherwise None.
    """
    action = "WRITE"
    if check_exists(filepath):
        action = "OVERWRITE"
    try:
        with open(filepath, "wb") as outfile:
            joblib.dump(content, outfile)
        print_io_status(filepath, action, status="SUCCESS")
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)


### TEXT
def read_text(filepath: str) -> str | None:
    """Reads a text file and returns its contents as a string.

    Args:
        filepath (str): The path to the text file to be read.

    Returns:
        str: The contents of the text file if read successfully,
        otherwise None.
    """
    action = "READ"
    try:
        with open(filepath, "r", encoding="utf-8") as file_in:
            content = file_in.read()
        print_io_status(filepath, action, status="SUCCESS")
        return content
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)
        return None


def write_text(content: str, filepath: str) -> None:
    """Writes the given string content to a text file.

    Args:
        content (str): The content to write to the text file.
        filepath (str): The path to the text file to be written.
    """
    action = "WRITE"
    if check_exists(filepath):
        action = "OVERWRITE"
    try:
        with open(filepath, "w+", encoding="utf-8") as outfile:
            outfile.write(content)
        print_io_status(filepath, action, status="SUCCESS")
    except Exception as e:
        print_io_status(filepath, action, status="FAIL", error=e)


### HDF5
#### .hdf5 files behave like python dictionaries


### HDF5
### Additional Context:
# 1. **HDF5 File Handling**:
#    - `h5py.File(filepath, 'r')`: Opens the HDF5 file in read mode.
#    - `file.create_dataset(key, data=value)`: Creates datasets in the HDF5 file with the data from the dictionary.

# 2. **Error Handling**:
#    - The code captures and logs any exceptions that occur during file operations, providing feedback via the `print_io_status` function.

# 3. **File Overwriting**:
#    - The `check_exists` function checks if a file already exists to change the `action` status to "OVERWRITE".


# def read_hdf5(filepath: str) -> dict | None:
#     """Reads an HDF5 file and returns its contents as a dictionary.

#     This function attempts to read an HDF5 file from the specified filepath.
#     If successful, it logs a "SUCCESS" status and returns the contents of the
#     file as a dictionary. If an error occurs, it logs a "FAIL" status.

#     Args:
#         filepath (str): The path to the HDF5 file to be read.

#     Returns:
#         dict: The contents of the HDF5 file if read successfully,
#         otherwise None.

#     Raises:
#         Exception: If any error occurs during reading the HDF5 file.
#     """
#     action = "READ"
#     try:
#         with h5py.File(filepath, "r") as file:
#             contents = {key: np.array(file[key]) for key in file.keys()}
#         print_io_status(filepath, action, status="SUCCESS")
#         return contents
#     except Exception as e:
#         print_io_status(filepath, action, status="FAIL", error=e)
#         return None


# def write_hdf5(content: dict, filepath: str) -> None:
#     """Writes the given dictionary to an HDF5 file.

#     Args:
#         content (dict): The dictionary to write to the HDF5 file. Each key-value pair
#             in the dictionary will be written as a dataset in the HDF5 file.
#         filepath (str): The path to the HDF5 file to be written.
#     """
#     action = "WRITE"
#     if check_exists(filepath):
#         action = "OVERWRITE"
#     try:
#         with h5py.File(filepath, "w") as file:
#             for key, value in content.items():
#                 file.create_dataset(key, data=value)
#         print_io_status(filepath, action, status="SUCCESS")
#     except Exception as e:
#         print_io_status(filepath, action, status="FAIL", error=e)


## These are for reading hdf5 into dataframes
# def read_hdf5(filepath: str, dataset: str) -> pd.DataFrame | None:
#     """Reads a dataset from an HDF5 file and returns its contents as a DataFrame.

#     This function attempts to read a specified dataset from an HDF5 file located
#     at the given filepath. If successful, it logs a "SUCCESS" status and returns
#     the contents of the dataset as a DataFrame. If an error occurs, it logs a "FAIL" status.

#     Args:
#         filepath (str): The path to the HDF5 file to be read.
#         dataset (str): The dataset within the HDF5 file to read.

#     Returns:
#         pd.DataFrame: The contents of the HDF5 dataset if read successfully,
#         otherwise None.

#     Raises:
#         Exception: If any error occurs during reading the HDF5 file.
#     """
#     action = "READ"
#     try:
#         with h5py.File(filepath, "r") as file:
#             data = file[dataset][...]
#             contents = pd.DataFrame(data)
#             print_io_status(filepath, action, status="SUCCESS")
#             return contents
#     except Exception as e:
#         print_io_status(filepath, action, status="FAIL", error=e)
#         return None


# def write_hdf5(content: pd.DataFrame, filepath: str, dataset: str) -> None:
#     """Writes the given DataFrame to an HDF5 file under the specified dataset name.

#     Args:
#         content (pd.DataFrame): The DataFrame to write to the HDF5 file.
#         filepath (str): The path to the HDF5 file to be written.
#         dataset (str): The dataset name to write the DataFrame into.
#     """
#     action = "WRITE"
#     if check_exists(filepath):
#         action = "OVERWRITE"
#     try:
#         with h5py.File(filepath, "a") as file:
#             if dataset in file:
#                 del file[dataset]  # Overwrite existing dataset
#             file.create_dataset(dataset, data=content.values)
#             print_io_status(filepath, action, status="SUCCESS")
#     except Exception as e:
#         print_io_status(filepath, action, status="FAIL", error=e)


###################################################################################################
### READ WRAPPER
def read_file(filepath: str) -> object | None:
    """Reads a file based on its extension and returns its contents.

    Args:
        filepath (str): The path to the file to be read.

    Returns:
        The contents of the file read based on its extension.
    """
    filetype = os.path.basename(filepath).split(".")[-1]
    if filetype == "csv":
        content = read_csv(filepath)
    elif filetype == "xlsx":
        content = read_xlsx(filepath)
    elif filetype == "parquet":
        content = read_parquet(filepath)
    elif filetype == "json":
        content = read_json(filepath)
    elif filetype == "joblib":
        content = read_joblib(filepath)
    elif filetype == "hdf5":
        content = read_hdf5(filepath)
    elif filetype == "py":
        content = read_text(filepath)
    else:
        content = read_text(filepath)
    return content


def write_file(content: object, filepath: str) -> None:
    """Writes content to a file based on its extension.

    Args:
        content: The content to write to the file.
        filepath (str): The path to the file to be written.
    """
    filetype = os.path.basename(filepath).split(".")[-1]
    if filetype == "csv":
        write_csv(content, filepath)
    elif filetype == "parquet":
        write_parquet(content, filepath)
    elif filetype == "json":
        write_json(content, filepath)
    elif filetype == "joblib":
        write_joblib(content, filepath)
    elif filetype == "hdf5":
        write_hdf5(content, filepath)
    else:
        write_text(content, filepath)


def read_database(filepath: str) -> sqlite3.Connection | None:
    """Attempts to connect to an SQLite database and returns the connection.

    Args:
        filepath (str): The path to the SQLite database file.

    Returns:
        sqlite3.Connection or None: The SQLite database connection if successful, otherwise None.
    """
    database = None
    if ".sqlite" in os.path.basename(filepath):
        try:
            database = sqlite3.connect(filepath)
            print("Connection to SQLite DB SUCCESS")
        except sqlite3.Error as e:
            print("Connection to SQLite DB FAILED")
            print(f"The error '{e}' occurred")
    return database


#### UNDER DEVELOPMENT

# from docx import Document
# document = Document("Resume_Erik_Hodges_Oct_2022.docx")
# document.save("GPT_Resume_Erik_Hodges_Oct_2022.docx")

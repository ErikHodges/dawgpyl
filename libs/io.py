## Common functions that are used across projects and classes

import json
import os

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

import sqlite3

import joblib
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from libs.common import print_log_entry

from typing import Callable, List, Optional, Dict, Any, Union, Annotated
import os
from pydantic import BaseModel, Field, model_validator

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------


def _get_name(variable: object = None) -> str:
    """Return the name attribute of a variable, if available."""
    return getattr(variable, "name", "Unknown")


def _get_class(class_name: str = None):
    """Return the class object given its name as a string."""
    return globals()[class_name]


def _get_abspath(*args, **kwargs) -> str:
    """
    Return the absolute path based on a provided 'path' keyword argument.

    Example:
        _get_abspath(path="relative/path.txt")
    """
    if kwargs:
        return os.path.abspath(kwargs.get("path"))
    elif args:
        return os.path.abspath(args[0])   


def _get_basename(*args, **kwargs) -> str:
    """
    Return the base name (the final component) of the given 'path'.

    Example:
        _get_basename(path="/full/path/to/file.txt")
    """
    if kwargs:
        return os.path.basename(kwargs.get("path"))
    elif args:
        return os.path.basename(args[0])


def _get_filetype(*args, **kwargs) -> str:
    """
    Return the file type (file extension) from the provided 'path'.

    Example:
        _get_type(path="/full/path/to/file.txt")  -> "txt"
    """
    if kwargs:
        path = kwargs.get("path")
    elif args: 
        path = args[0]    
    return os.path.basename(path).split(".")[-1] if "." in path else ""


def _check_exists(*args, **kwargs) -> bool:
    """
    Check if a file exists at the specified filepath.

    Args:
        path (str): The path to the file.

    Returns:
        bool: True if the file exists, otherwise False.
    """
    if kwargs:
        return os.path.exists(kwargs.get("path"))
    elif args:    
        return os.path.exists(args[0])
    else:
        return False


def _print_io_status(filepath: str, action: str, status: str, **kwargs) -> None:
    """
    Print the status of an I/O operation.

    Args:
        filepath (str): The file path.
        action (str): The action performed (e.g., READ, WRITE).
        status (str): The status of the action (e.g., SUCCESS, FAIL).
        error (Exception, optional): The error encountered (if any).
    """
    error = kwargs.get("error", None)
    if error:
        print(f"{action} {status}:\n{filepath}\nError: {error}")
    else:
        print(f"{action} {status}:\n{filepath}")


# -----------------------------------------------------------------------------
# I/O Classes
# -----------------------------------------------------------------------------


class IO(BaseModel):
    """
    Base class for file I/O operations.

    This class defines the basic structure and interface for file readers
    and writers. Specific file types should subclass IO and implement
    the read and write methods.
    """

    path: str = Field(default="", description="The path to the file to process.")
    filetype: str = Field(default="txt", description="The filetype of file to process.")
    status: str = Field(default="SUCCESS", description="The status of the I/O operation.")

    def read(self, filepath: Optional[str] = None, **kwargs) -> Any:
        """
        Read the file content.

        This method is expected to be overridden by subclasses.
        """
        raise NotImplementedError("The read method must be implemented in the subclass.")

    def write(self, filepath: Optional[str] = None, data: Any = None, **kwargs) -> None:
        """
        Write data to the file.

        This method is expected to be overridden by subclasses.
        """
        raise NotImplementedError("The write method must be implemented in the subclass.")


class IOtext(IO):
    """
    I/O class for handling text files.

    Inherits from IO and implements the read and write methods using standard Python I/O.
    """

    filetype: str = Field(
        default="txt", frozen=True, description="File type, frozen as 'txt' for text files."
    )

    def read(self, filepath: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        Reads a text file and returns its contents as a string.

        Args:
            filepath (str, optional): The path to the text file. If not provided,
                                      the instance's `path` attribute is used.
            encoding (str): The file encoding (default is "utf-8").

        Returns:
            Optional[str]: The contents of the file, or None if reading fails.
        """
        action = "READ"
        target_path = filepath or self.path
        encoding = kwargs.get("encoding", "utf-8")
        try:
            with open(target_path, "r", encoding=encoding) as file_in:
                content = file_in.read()
            _print_io_status(target_path, action, "SUCCESS")
            return content
        except Exception as e:
            _print_io_status(target_path, action, "FAIL", error=e)
            return None

    def write(self, filepath: Optional[str] = None, data: str = "", **kwargs) -> None:
        """
        Writes a string to a text file.

        Args:
            filepath (str, optional): The path to the text file. If not provided,
                                      the instance's `path` attribute is used.
            data (str): The text content to write.
        """
        action = "WRITE"
        target_path = filepath or self.path
        if _check_exists(target_path):
            action = "OVERWRITE"
        try:
            with open(target_path, "w+", encoding="utf-8") as outfile:
                outfile.write(data)
            _print_io_status(target_path, action, "SUCCESS")
        except Exception as e:
            _print_io_status(target_path, action, "FAIL", error=e)


def _get_io(self) -> IO:
    """
    Factory method to return an instance of the appropriate I/O subclass
    based on the file type.
    """
    io_map: Dict[str, Callable[..., IO]] = {
        "txt": IOtext,
        # "json": IOjson,     # You can add additional mappings here.
        # "csv": IOcsv,
        # "sqlite": IOsqlite,
        # "joblib": IOjoblib,
        # "parquet": IOparquet,
    }
    # Choose the I/O class based on file extension, defaulting to IOtext if not found.
    io_class = io_map.get(self.filetype.lower(), IOtext)
    return io_class(path=self.path)


# -----------------------------------------------------------------------------
# File Class
# -----------------------------------------------------------------------------


class File(BaseModel):
    """
    Class for file configuration.

    This class uses helper functions to initialize attributes like path,
    name, type, and existence. It also creates an appropriate I/O handler
    based on the file type (currently only text files are supported).
    """
   
    
    path: Annotated[str, Field(description="The full path to the file.")]
    basename:  Annotated[Optional[str], Field(default=None, description="The name of the file.")]
    filetype: Annotated[Optional[str], Field(default=None, description="The file extension/type.")]
    exists: Annotated[Optional[bool], Field(default=None, description="Indicates whether the file exists.")]
    io: Annotated[Optional[IO], Field(default=None, description="The I/O handler for the file.")]
    content: Annotated[Optional[Any], Field(default=None, description="The content of the file after reading.")]

    @model_validator(mode='after')    
    def _validate(self) -> str:
        self.path = _get_abspath(self.path)
        self.basename = _get_basename(self.path)
        self.filetype = _get_filetype(self.path)
        self.exists = _check_exists(self.path)
        self.io = _get_io(self)
        return self

    def read(self) -> Any:
        """
        Reads the file content using the I/O handler.

        Returns:
            The content read from the file.
        """
        if self.io:
            self.content = self.io.read()

    def write(self, content: Any) -> None:
        """
        Writes data to the file using the I/O handler.

        Args:
            content: The data to write to the file.
        """
        if self.io:
            self.io.write(content=content)
            self.content = content







###################################################################################################
### File Conversions

# def img2b64(img_path):
#     """Convert image to base64 string"""
#     with open(img_path, "rb") as image_file:
#         b64_string = base64.b64encode(image_file.read())
#     return b64_string


# def b642img(b64_string, img_path):
#     """Convert base64 string to image"""
#     with open(img_path, "wb") as fh:
#         fh.write(base64.decodebytes(b64_string))
#     return print(f"The variable '{get_varname(b64_string)}' has been written to {img_path}")


# def html2md(html_path: str):
#     """Function to convert html webpage (saved manually) to a markdown format"""
#     html_string = file_open(html_path)
#     md_string = markdownify(html_string)

#     basename_html = os.path.basename(html_path)
#     basename_md = basename_html.replace(".html", ".md")
#     out_path = html_path.replace(basename_html, basename_md)
#     write_file(md_string, out_path)
#     print(f"File saved to: {out_path}")

#     return md_string


# def url2md(url: str, output_basename: str):
#     """At some point I'll want to make it so that my url2md function can iterate over a list of pages"""
#     response = urllib.request.urlopen(url)
#     html_string = response.read().decode("UTF-8")

#     md_string = markdownify(html_string)

#     file_save(md_string, f"{output_basename}.md")


###################################################################################################
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
        _print_io_status(filepath, action, status="SUCCESS")
        return contents
    except Exception as e:
        _print_io_status(filepath, action, status="FAIL", error=e)
        return None


def write_csv(content: pd.DataFrame, filepath: str) -> None:
    """Writes the given DataFrame to a CSV file.

    Args:
        content (pd.DataFrame): The DataFrame to write to the CSV file.
        filepath (str): The path to the CSV file to be written.
    """
    action = "WRITE"
    if _check_exists(filepath):
        action = "OVERWRITE"
    try:
        content.to_csv(filepath, header=True, index=False)
        _print_io_status(filepath, action, status="SUCCESS")
    except Exception as e:
        _print_io_status(filepath, action, status="FAIL", error=e)


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
        _print_io_status(filepath, action, status="SUCCESS")
        return contents
    except Exception as e:
        _print_io_status(filepath, action, status="FAIL", error=e)
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
        _print_io_status(filepath, action, status="SUCCESS")
        return contents
    except Exception as e:
        _print_io_status(filepath, action, status="FAIL", error=e)
        return None


def write_parquet(content: pd.DataFrame | pa.Table, filepath: str) -> None:
    """Writes the given DataFrame or PyArrow Table to a Parquet file.

    Args:
        content (pd.DataFrame or pa.Table): The content to write to the Parquet file.
        filepath (str): The path to the Parquet file to be written.
    """
    action = "WRITE"
    if _check_exists(filepath):
        action = "OVERWRITE"
    try:
        if isinstance(content, pd.DataFrame):
            df_pa = pa.Table.from_pandas(content)
            pq.write_table(df_pa, filepath)
        elif isinstance(content, pa.Table):
            pq.write_table(content, filepath)
        _print_io_status(filepath, action, status="SUCCESS")
    except Exception as e:
        _print_io_status(filepath, action, status="FAIL", error=e)


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
            _print_io_status(filepath, action, status="SUCCESS")
        return content
    except Exception as e:
        _print_io_status(filepath, action, status="FAIL", error=e)
        return None


def write_json(content: dict, filepath: str) -> None:
    """Writes the given dictionary to a JSON file.

    Args:
        content (dict): The content to write to the JSON file.
        filepath (str): The path to the JSON file to be written.
    """
    action = "WRITE"
    if _check_exists(filepath):
        action = "OVERWRITE"
    try:
        if (isinstance(content, dict)) and (".json" in os.path.basename(filepath)):
            content = json.dumps(content)
        with open(filepath, "w+", encoding="utf-8") as outfile:
            json.dump(content, outfile, indent=4)
        _print_io_status(filepath, action, status="SUCCESS")
    except Exception as e:
        _print_io_status(filepath, action, status="FAIL", error=e)


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
        _print_io_status(filepath, action, status="SUCCESS")
        return content
    except Exception as e:
        _print_io_status(filepath, action, status="FAIL", error=e)
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
    if _check_exists(filepath):
        action = "OVERWRITE"
    try:
        with open(filepath, "wb") as outfile:
            joblib.dump(content, outfile)
        _print_io_status(filepath, action, status="SUCCESS")
    except Exception as e:
        _print_io_status(filepath, action, status="FAIL", error=e)



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


###################################################################################################
### LOG
def read_log_file(filepath: str):
    if _check_exists(filepath):
        print("LOG FILE FOUND")
        print()
        try:
            log = read_file(filepath)
            try:
                print_log_entry(log)
            except:
                print(log)
        except:
            pass
    else:
        log = None
        print("LOG FILE NOT FOUND")
    return log


#### UNDER DEVELOPMENT

# from docx import Document
# document = Document("Resume_Erik_Hodges_Oct_2022.docx")
# document.save("GPT_Resume_Erik_Hodges_Oct_2022.docx")

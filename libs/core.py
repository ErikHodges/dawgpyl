"""This module contains the base and extended classes for general AI agent workflow development."""

import json
import os
import warnings
from dataclasses import dataclass
from datetime import datetime as dt
from uuid import uuid4

import pandas as pd
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.runnables import chain
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langsmith import traceable
from termcolor import colored

from configs.apis import *
from configs.core import *

pd.set_option("mode.copy_on_write", True)


###################################################################################################
### Base Classes
#### This module contains the base (core) and extended classes for general AI agent workflow development.


@dataclass(slots=False)
class Directories:
    """Class for handling directory paths related to the project."""

    root: str
    libs: str
    security: str
    configs: str
    data: str
    docs: str
    databases: str
    models: str
    inputs: str
    outputs: str
    logs: str
    out_files: str

    def __init__(self) -> None:
        """Initializes the Directories class with the given project name.

        Args:
            None
        """
        self.get_directories()

    def get_directories(self) -> None:
        """Initializes and sets the directory paths.

        Args:
            None
        """
        self.root = os.getcwd()

        self.libs = os.path.join(self.root, "libs")
        self.security = os.path.join(self.root, "security")
        self.configs = os.path.join(self.root, "configs")
        self.models = os.path.join(self.root, "models")

        self.data = os.path.join(self.root, "data")
        self.docs = os.path.join(self.data, "docs")
        self.databases = os.path.join(self.data, "databases")
        self.logs = os.path.join(self.data, "logs")
        self.inputs = os.path.join(self.data, "inputs")
        self.outputs = os.path.join(self.data, "outputs")
        self.out_files = os.path.join(self.outputs, "files")


@dataclass(slots=False)
class Timestamp:
    """Class for creating and handling timestamps."""

    datetime: dt
    iso: str
    date: str
    time: str
    filestamp: str
    timezone: str
    utc_offset: str

    def __init__(self) -> None:
        """Initializes the Timestamp class."""
        self.create()

    def create(self) -> None:
        """Generates the current time in various formats."""
        self.datetime = dt.now(dt.now().astimezone().tzinfo)
        self.iso = self.datetime.isoformat()
        self.date = self.datetime.strftime("%Y-%m-%d")
        self.time = self.datetime.strftime("%H:%M:%S")
        self.filestamp = self.datetime.strftime("%Y-%m-%dT%H-%M-%S")
        self.timezone = self.datetime.strftime("%Z")
        self.utc_offset = self.datetime.strftime("%z")


@dataclass(slots=False)
class Target:
    """Class representing a single log entry."""

    type: str
    name: str

    def __init__(self, target_class: str, name: str) -> None:
        """Initializes the Target class.

        Args:
            target_class (str): The class of the target.
            name (str): The name of the target.
        """
        self.type = target_class
        self.name = name


@dataclass(slots=False)
class Event:
    """Class representing a single log entry."""

    timestamp: str
    target: str
    event: str

    def __init__(self, target: Target, action: str) -> None:
        """Initializes the Event class.

        Args:
            target (Target): The target of the event.
            action (str): The description of the event.
        """
        self.timestamp = Timestamp().iso
        self.target = f"{target.type}('{target.name}')"
        self.event = action

    def unpack(self) -> dict:
        """Unpacks the event details into a dictionary.

        Returns:
            dict: A dictionary containing the event details.
        """
        return {"timestamp": self.timestamp, "target": self.target, "event": self.event}


@dataclass(slots=False)
class Log:
    """Class that maintains a history of events."""

    history: list
    last: dict

    def __init__(self) -> None:
        """Initializes the Log class."""
        event = Event(Target(get_class(self), "Log"), "started")
        self.history = [
            {"timestamp": event.timestamp, "target": event.target, "event": event.event}
        ]
        self.last = self.history[-1]

    def update_last(self) -> None:
        """Updates the last event in the log."""
        self.last = self.history[-1]

    def add(self, event: Event) -> None:
        """Records an event in the log.

        Args:
            event (Event): The event to be recorded.
        """
        self.history.append(event.unpack())
        self.update_last()

    def search_log_targets(self, term: str) -> list:
        """Searches the log for events with a specific target.

        Args:
            term (str): The term to search for in the target.

        Returns:
            list: A list of log events that match the search term.
        """
        log_search_results = []
        for idx, log_event in enumerate(self.history):
            if term in log_event["target"]:
                log_search_results.append(log_event)
        return log_search_results

    def search(self, term: str) -> list:
        """Searches the log for events with a specific description.

        Args:
            term (str): The term to search for in the event description.

        Returns:
            list: A list of log events that match the search term.
        """
        search_results = []
        for idx, log_event in enumerate(self.history):
            if term in log_event["event"]:
                search_results.append(log_event)
        return search_results


# @dataclass(slots=False)
# class StatusLog(Log):
#     """Class that maintains a history of status events."""

#     history: list
#     log: Log

#     def __init__(self, name: str) -> None:
#         """Initializes the StatusLog class.

#         Args:
#             name (str): The name of the status log.
#         """
#         self.name = name
#         self.status = "status_registered"


# NOTE: I believe the MessageLog should inherit from the Log class
@dataclass(slots=False)
class MessageLog:
    """Class for storing agent messages."""

    history: list
    last: dict
    last_message: str | None

    def __init__(self) -> None:
        """Initializes the MessageLog class."""
        self.history = []
        self.last = {}
        self.last_message = None

    def update_last(self) -> None:
        """Updates the last message in the log."""
        self.last = self.history[-1]
        self.last_message = self.last["message"] or None

    def add_message(self, message: str) -> None:
        """Adds a message to the log.

        Args:
            message (str): The message to be added.
        """
        self.history.append(
            {
                "timestamp": Timestamp().iso,
                "message": message,
            }
        )
        self.update_last()

    def search_messages(self, term: str) -> list:
        """Searches the log for messages containing a specific term.

        Args:
            term (str): The term to search for in the messages.

        Returns:
            list: A list of messages that match the search term.
        """
        message_search_results = []
        for msg_idx, message in enumerate(self.history):
            if term in message["message"]:
                message_search_results.append(self.history[msg_idx])
        return message_search_results


# NOTE: I believe the TeamMessageLog should inherit from the Log class
@dataclass(slots=False)
class TeamMessageLog:
    """Class for storing team messages."""

    history: dict
    last: dict

    def __init__(self) -> None:
        """Initializes the TeamMessageLog class."""
        self.history = {}
        self.last = {}

    def search_team_messages_content(self, term: str) -> list:
        """Searches the group messages for content containing a specific term.

        Args:
            term (str): The term to search for in the group messages.

        Returns:
            list: A list of group messages that match the search term.
        """
        team_message_search_results = []
        for msg_idx, message in enumerate(self.history):
            if term in message["message"]:
                team_message_search_results.append(self.history[msg_idx])
        return team_message_search_results


###################################################################################################
### Task Classes
#### This module contains the Task class, used to store task information.


@dataclass(slots=False)
class Task:
    """Class for storing task information."""

    name: str | None
    priority: int | None
    objective: str | None
    assignee: str | None
    finished: bool | None
    event: Event | None
    log: Log | None

    def __init__(
        self,
        persona: str = "default",
        assignee="task_manager",
        **kwargs,
    ):

        self.name = str(uuid4())
        self.priority = 1
        self.assignee = assignee
        self.finished = False
        if kwargs.get("objective", None):
            self.objective = kwargs.get("objective")
        else:
            try:
                self.objective = TASKS[persona]
            except:
                self.objective = TASKS["default"]
        self.event = Event(
            Target(get_class(self), self.name), f"objective created: {self.objective}"
        )
        self.log = Log()
        ###def __post_init__(self):
        self.log.add(self.event)

    def update_objective(self, new_objective):
        self.objective = new_objective
        self.event = Event(
            Target(get_class(self), self.name), f"objective changed: {new_objective}"
        )
        self.log.add(self.event)

    def assign(self, assignee=None):
        self.assignee = assignee
        self.event = Event(Target(get_class(self), self.name), f"assignee changed: {self.assignee}")
        self.log.add(self.event)

    def log_event(self, event_description):
        self.event = Event(Target(get_class(self), self.name), event_description)
        self.log.add(self.event)

    def prioritize(self):
        """Sets the task to highest priority."""
        self.priority = 0
        self.event = Event(Target(get_class(self), self.name), "task prioritized")
        self.log.add(self.event)

    def set_finished(self):
        """Sets the task to finished."""
        self.priority = 1
        self.finished = True
        self.event = Event(Target(get_class(self), self.name), "task finished")
        self.log.add(self.event)


###################################################################################################
### Tool Classes
#### This module contains the Tool class, used to define the tools that are assigned to agents.
#### note: Not implemented, WIP

# def search_web(search_str: str):
#     return print(f"Searching for: {search_str}")


# def scrape_website(url):
#     try:
#         # Fetch the web page content
#         response = requests.get(url)
#         response.raise_for_status()
#         # Parse the HTML content using BeautifulSoup
#         soup = BeautifulSoup(response.text, "html.parser")
#         # Extract the text from the HTML
#         text = " ".join([p.get_text() for p in soup.find_all("p")])
#         return text
#     except Exception as e:
#         return str(e)


# def describe_tool(tool):
#     tool_description = tool.__doc__
#     return tool_description

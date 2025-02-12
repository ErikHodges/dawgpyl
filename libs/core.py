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
### Agent Classes
#### This module contains the Agent class, used in single-agent and multi-agent workflows.


# NOTE: this could probably be in the common library
def strip_self_refs(self_reference: str) -> str:
    """Replaces periods in self-references with underscores.

    Args:
        self_reference (str): The self-reference string to be modified.

    Returns:
        str: The modified self-reference string.
    """
    self_reference = self_reference.replace(".", "_")
    return self_reference


@dataclass(slots=False)
class AgentConfig:
    """Class for storing agent configuration settings."""

    priority: int
    needs_review: bool
    model: Model
    prompt_params: list
    prompt_arg_vals: dict
    prompt_template: str
    response_format: dict
    response_template: dict
    tools: list
    seed: int
    temperature: float
    top_p: float
    max_tokens: int
    max_retries: int
    timeout: int

    def __init__(self, name: str = "default") -> None:
        """Initializes the AgentConfig with the given name.

        Args:
            name (str): The name of the agent configuration. Defaults to "default".
        """
        agent_config = AGENTS[name]
        agent_parameters = AGENTS[name]["parameters"]
        self.priority = agent_config["priority"]
        self.needs_review = agent_config["needs_review"]
        self.model = Model(agent_config["model"])
        self.prompt_params = agent_config["prompt_params"]
        self.prompt_arg_vals = {}
        self.prompt_template = agent_config["prompt_template"]
        self.response_format = agent_parameters.get("response_format")
        self.response_template = agent_config["response_template"]
        self.tools = agent_config["tools"]
        self.seed = agent_parameters["seed"]
        self.temperature = agent_parameters.get("temperature")
        self.top_p = agent_parameters.get("top_p")
        self.max_tokens = agent_parameters.get("max_tokens")
        self.max_retries = agent_parameters.get("max_retries")
        self.timeout = agent_parameters.get("timeout")

    def __print__(self) -> None:
        """Prints the agent configuration."""
        return print(self.__dict__)


@dataclass(slots=False)
class Agent:
    """Class for storing agent information."""

    name: str | None
    config: AgentConfig | None
    task: Task | None
    needs_review: bool | None
    project: dict | None
    team: dict | None
    teammates: list | None
    model: Model | None
    inputs: MessageLog | None
    prompt: str | None
    outputs: MessageLog | None
    final_answer: str | None
    status: dict | None
    finished: bool
    tools: list | None
    event: Event | None
    log: Log | None

    def __init__(self, name: str = "default", agent_config: str = None) -> None:
        """Initializes the Agent with the given name and configuration.

        Args:
            name (str): The name of the agent. Defaults to "default".
            agent_config (str, optional): The agent configuration name. Defaults to None.
        """
        self.name = name
        if agent_config:
            self.config = AgentConfig(agent_config)
        else:
            self.config = AgentConfig(name)
        self.needs_review = self.config.needs_review
        self.project = None
        self.team = None
        self.teammates = []
        self.task = Task(persona=name)
        self.finished = False
        self.model = self.config.model
        self.prompt = None
        self.inputs = MessageLog()
        self.outputs = MessageLog()
        self.final_answer = None
        self.status = {name: "agent initialized"}
        self.tools = self.config.tools
        self.event = Event(Target(get_class(self), self.name), self.status[name])
        self.log = Log()
        self.log.add(self.event)
        self.fetch_model_client()

    def log_agent(self, event_description: str) -> None:
        """Logs an event for the agent.

        Args:
            event_description (str): The description of the event.
        """
        self.event = Event(Target(get_class(self), self.name), event_description)
        self.log.add(self.event)

    def fetch_model_client(self) -> None:
        """Fetches the model client for the agent."""
        self.model.instantiate_client(self.config)
        self.log_agent("client initialized")

    def fetch_team_name(self) -> str:
        """Fetches the team name.

        Returns:
            str: The team name.
        """
        return self.team.name

    def fetch_project_name(self) -> str:
        """Fetches the project name.

        Returns:
            str: The project name.
        """
        return self.project.name

    def fetch_prompt_arg_vals(self) -> None:
        """Fetches the prompt argument values for the agent."""
        self.config.prompt_arg_vals = {}
        empty_data_types = {
            str: "",
            list: [],
            dict: {},
            type(None): None,
        }
        for arg in self.config.prompt_params:
            arg_val = eval(arg)
            if arg_val == empty_data_types[type(arg_val)]:
                arg_val = "None"
            self.config.prompt_arg_vals[strip_self_refs(arg)] = arg_val

    def format_prompt(self) -> None:
        """Formats the prompt for the agent."""
        self.fetch_prompt_arg_vals()
        self.prompt = self.config.prompt_template.format(**self.config.prompt_arg_vals)

    def change_status(self, new_status: str) -> None:
        """Changes the status of the agent.

        Args:
            new_status (str): The new status of the agent.
        """
        self.status[self.name] = new_status
        self.log_agent(new_status)

    def parse_review(self) -> str:
        """Parses the review status from the agent's outputs.

        Returns:
            str: The review status.
        """
        if self.outputs.last_message:
            try:
                pass_review = self.outputs.last_message["pass_review"]
            except KeyError:
                pass_review = False
        else:
            pass_review = False

        return str(pass_review)

    def check_finished(self) -> str:
        """Checks if the agent has finished its task.

        Returns:
            str: The finished status.
        """
        is_finished = str(False)
        try:
            if self.inputs.last["message"]["pass_review"]:
                self.final_answer = self.outputs.last["message"]
                self.change_status("finished")
                self.finished = True
                is_finished = "True"
                self.team.members_finished.append(self.name)
        except KeyError:
            pass
        return is_finished

    def get_status(self) -> dict:
        """Gets the current status of the agent.

        Returns:
            dict: The current status of the agent.
        """
        return self.status

    def fetch_content_for_review(self) -> None:
        """Fetches content for review if the agent is a reviewer."""
        if "_reviewer" in self.name:
            try:
                agent2review = self.name.replace("_reviewer", "")
                self.inputs.add_message(self.team.outputs.last[agent2review]["message"])
            except KeyError:
                print("unable to fetch content for review")

    @traceable  # Auto-trace this function
    def invoke(self, *args, **kwargs) -> dict:
        """Invokes the agent to perform its task.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: The updated project and team information.
        """
        for arg in args:
            pass
        for kwarg in kwargs:
            pass
        # cur_kwargs = {name: kwargs.pop(name) for name in kwargs if name in kwargs}

        self.check_finished()
        if not self.finished:
            self.team.update()
            self.project.update()
            self.fetch_content_for_review()
            self.change_status("invoked")
            self.format_prompt()
            full_response = self.model.client.invoke(self.prompt)
            expected_response_type = self.config.response_format["type"]
            message = parse_agent_response(full_response, expected_response_type)
            token_usage = json.dumps(full_response.response_metadata["token_usage"])
            self.outputs.add_message(message)
            self.log_agent(f"message: {message}")
            self.log_agent(f"tokens: {token_usage}")
            self.change_status("responded")
            if not self.needs_review:
                self.final_answer = self.outputs.last["message"]
                self.change_status("finished")
                self.finished = True
        else:
            full_response = self.outputs.last
            message = self.final_answer
        # TODO: Make sure I'm not overwriting the project state at this point
        self.team.update()
        self.project.update()
        return {"project": self.project, "team": self.team}


def create_agent(agent_name: str) -> tuple:
    """Creates an agent with the given name.

    Args:
        agent_name (str): The name of the agent.

    Returns:
        tuple: The created agent and its model configuration.
    """
    print_heading(f"Agent({repr(agent_name)}): Model Config", "green")
    agent = Agent(agent_name)
    model_config = agent.config.model.__dict__
    model_config = {
        "type": model_config["type"],
        "api": model_config["api"],
        "name": model_config["name"],
        "size": model_config["size"],
        "max_tokens": agent.config.max_tokens,
        "temperature": agent.config.temperature,
        "max_retries": agent.config.max_retries,
        "timeout": agent.config.timeout,
        "response_format": agent.config.response_format,
    }
    print_dict(model_config, "green")
    return agent, model_config


def invoke_agent(agent: Agent, *args, **kwargs) -> tuple:
    """Invokes the agent with the given arguments and keyword arguments.

    Args:
        agent (Agent): The agent to be invoked.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        tuple: The response and model artifact.
    """
    model_config = kwargs.get("model_config", None)
    response_format = kwargs.get("response_format", None)
    prompt = kwargs.get("prompt", None)
    log_file_path = kwargs.get("log_file_path", None)
    save_log = kwargs.get("save_log", None)

    agent.config.response_format = response_format
    agent.fetch_model_client()

    full_response = agent.model.client.invoke(prompt)
    response = full_response.__dict__
    print_heading("Tokens", "blue")
    print_dict(full_response.usage_metadata, "blue")
    print_heading(f"Agent('{agent.name} - RESPONSE')", "green")
    print(colored(full_response.content, "green"))
    print("\n")

    if save_log:
        log = read_file(log_file_path)
        log = eval(log.replace("log = ", ""))
        model_artifact = {
            "run_datetime": Timestamp().iso,
            "model_config": model_config,
            "user_prompt": prompt,
            "final_response": full_response.content,
        }
        log.append(model_artifact)
        log_text = f"log = {log}"
        write_file(log_text, log_file_path)
    return response, model_artifact


# def get_message(...):
#     from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


###################################################################################################
### Project Classes
#### This module contains the Project class, used to store the state of multiple multi-agent workflows.


@dataclass(slots=False)
class ProjectConfig:
    """Class for storing agent configuration settings."""

    name: str
    manager: str
    teams: list

    def __init__(self, name: str = "default") -> None:
        """
        Initializes the ProjectConfig with the given name.

        Args:
            name (str): The name of the project configuration. Defaults to "default".
        """
        project_config = PROJECTS[name]
        self.name = name
        self.manager = project_config["manager"]
        self.teams = project_config["teams"]

    def __print__(self) -> None:
        """Prints the dictionary representation of the ProjectConfig."""
        return print(self.__dict__)


@dataclass(slots=False)
class Project:
    """Class for storing task information."""

    name: str | None
    config: ProjectConfig | None
    manager: str | None
    goal: str | None
    plan: str | None
    backlog: dict | None  # A dict with top-level key for each team, and subkeys for each task-id
    teams: list | None
    inputs: TeamMessageLog | None
    outputs: TeamMessageLog | None
    final_answers: dict | None
    event: Event | None
    log: Log | None

    def __init__(self, name: str = "default", goal: str = "Be helpful!") -> None:
        """
        Initializes the Project with the given name and goal.

        Args:
            name (str): The name of the project. Defaults to "default".
            goal (str): The goal of the project. Defaults to "Be helpful!".
        """
        self.name = name
        self.config = ProjectConfig(name)
        self.manager = self.config.manager
        self.goal = goal
        self.plan = None
        self.backlog = {}
        self.teams = []
        self.inputs = TeamMessageLog()
        self.outputs = TeamMessageLog()
        self.final_answers = {}
        self.event = Event(Target(get_class(self), self.name), "created")
        self.log = Log()
        self.log.add(self.event)
        self.assemble_teams()
        self.request_introductions()
        # self.fetch_model_clients()
        self.update()

    def log_event(self, event_description: str) -> None:
        """
        Logs an event with the given description.

        Args:
            event_description (str): The description of the event.
        """
        self.event = Event(Target(get_class(self), self.name), event_description)
        self.log.add(self.event)

    def add_team(self, team2add: str = "default") -> None:
        """
        Adds a team to the project.

        Args:
            team2add (str): The name of the team to add. Defaults to "default".
        """
        self.teams.append(Team(project=self, config_name=team2add))
        self.log_event(f"added Team('{team2add}')")

    def assemble_teams(self) -> None:
        """Assembles teams based on the project configuration."""
        for team in self.config.teams:
            self.add_team(team)
        self.log_event("project teams assembled")

    def get_team_names(self) -> list:
        """
        Gets the names of all teams in the project.

        Returns:
            list: A list of team names.
        """
        return [x.name for x in self.teams]

    def return_self(self) -> "Project":
        """
        Returns the current instance of the Project.

        Returns:
            Project: The current instance of the Project.
        """
        return self

    def push_project_updates(self) -> None:
        """Pushes project updates to all teams and their members."""
        for team in self.teams:
            team.project = self.return_self()
            for member in team.members:
                member.project = self.return_self()

    def request_introductions(self) -> None:
        """Requests introductions from all team members."""
        for team in self.teams:
            for member in team.members:
                member.project = self
                member.teammates = team.fetch_member_names()
                member.outputs.add_message(
                    f"Hello! I'm on team '{team.name}', and my name is '{member.name}'"
                )
        self.log_event("project teams assembled")

    def fetch_final_answers(self) -> None:
        """Fetches final answers from all teams."""
        for team in self.teams:
            if team.final_answers and len(team.final_answers.keys()) > 0:
                self.final_answers[team.name] = team.final_answers

    def fetch_plan_goals(self) -> None:
        """Fetches plan and goals from final answers of all teams."""
        for team_name in self.get_team_names():
            if self.plan is not None:
                if self.final_answers and self.final_answers[team_name]:
                    try:
                        self.plan = self.final_answers[team_name]["project_manager"]
                    except KeyError:
                        self.plan = None
            if self.goal is not None:
                if self.final_answers and self.final_answers[team_name]:
                    try:
                        self.goal = self.final_answers[team_name]["goal_engineer"]
                    except KeyError:
                        self.goal = None

    def update(self) -> None:
        """Updates the project by fetching logs and final answers from all teams."""
        for team in self.teams:
            team.update()

            # fetch input log from each team
            if len(team.inputs.history) > 0:
                self.inputs.history[team.name] = team.inputs.history
            if len(team.inputs.last.keys()) > 0:
                self.inputs.last[team.name] = team.inputs.last

            # fetch output log from each team
            if len(team.outputs.history) > 0:
                self.outputs.history[team.name] = team.outputs.history
            if len(team.outputs.last.keys()) > 0:
                self.outputs.last[team.name] = team.outputs.last
            # fetch final answers from each team
            self.fetch_final_answers()
        self.push_project_updates()

    def __call__(self, *args, **kwargs) -> dict:
        """
        Updates the project and returns the current instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: A dictionary containing the current instance of the Project.
        """
        for arg in args:
            pass
        for kwarg in kwargs:
            pass
        self.update()
        return {"project": self.return_self()}

    # def compile_graphs(self):
    #     for team in self.teams:
    #         team_graph = create_team_graph(team)
    #         workflow = compile_workflow(team_graph)

    # def fetch_model_clients(self):
    #     for team in self.teams:
    #         for member in team.members:
    #             member.model.get_model_client(member.config)
    #             member.log_event("model client connected")

    # def fetch_member_messages(self,team,member_name):
    #     member_names = self.messages.get


###################################################################################################
### Team Classes
#### This module contains the Team class, used to store the state of multi-agent workflows.


@dataclass(slots=False)
class TeamConfig:
    """Class for storing agent configuration settings."""

    name: str
    leader: str
    members: list
    graph_config: dict

    def __init__(self, name: str = "default") -> None:
        """
        Initializes the TeamConfig with the given name.

        Args:
            name (str): The name of the team configuration. Defaults to "default".
        """
        team_config = TEAMS[name]
        self.name = name
        self.leader = team_config["leader"]
        self.members = team_config["members"]
        self.graph_config = team_config["graph_config"]


@dataclass(slots=False)
class Team:
    """Class for managing a team of agents.
    The name of the team determines the config that is retrieved"""

    name: str | None
    config: TeamConfig | None
    project: dict | None
    leader: str | None
    members: list | None
    members_finished: list | None
    goal: str | None
    backlog: dict | None
    task_assignments: dict | None
    inputs: TeamMessageLog | None
    outputs: TeamMessageLog | None
    final_answers: dict | None
    event: Event | None
    log: Log | None

    def __init__(self, project: dict, config_name: str = "default") -> None:
        """
        Initializes the Team with the given project and configuration name.

        Args:
            project (dict): The project details.
            config_name (str): The name of the team configuration. Defaults to "default".
        """
        self.name = generate_random_name()
        self.config = TeamConfig(config_name)
        self.project = project
        self.leader = self.config.leader
        self.members = []
        self.members_finished = []
        self.goal = None
        self.backlog = {}
        self.task_assignments = {}
        self.inputs = TeamMessageLog()
        self.outputs = TeamMessageLog()
        self.final_answers = {}
        self.event = Event(Target(get_class(self), self.name), "created")
        self.log = Log()
        self.log.add(self.event)
        self.assemble_team()
        self.update()

    def add_member(self, agent2add: str = "default") -> None:
        """
        Adds a member to the team.

        Args:
            agent2add (str): The name of the agent to add. Defaults to "default".
        """
        self.members.append(Agent(agent2add))
        self.event = Event(Target(get_class(self), self.name), f"added Agent('{agent2add}')")
        self.log.add(self.event)

    def add_reviewer(self, agent2review: str) -> None:
        """
        Adds a reviewer to the team.

        Args:
            agent2review (str): The name of the agent to review.
        """
        reviewer_name = f"{agent2review}_reviewer"
        self.members.append(Agent(name=reviewer_name, agent_config="reviewer"))
        self.event = Event(Target(get_class(self), self.name), f"added Agent('{reviewer_name}')")
        self.log.add(self.event)

    def get_member_index(self, member_name: str = "") -> int:
        """
        Gets the index of a member in the team.

        Args:
            member_name (str): The name of the member.

        Returns:
            int: The index of the member.
        """
        member_order = self.fetch_member_names()
        member_index = member_order.index(member_name)
        return member_index

    def check_finished(self, member_name: str = "") -> str:
        """
        Checks if a member has finished their task.

        Args:
            member_name (str): The name of the member.

        Returns:
            str: "True" if the member has finished, otherwise "False".
        """
        member_index = self.get_member_index(member_name)
        if self.members[member_index].finished:
            return str(True)
        else:
            return str(False)

    def assemble_team(self) -> None:
        """
        Assembles the team by adding members and reviewers if needed.
        """
        for member in self.config.members:
            self.add_member(member)
            if self.members[-1].needs_review:
                self.add_reviewer(agent2review=member)
        self.event = Event(Target(get_class(self), self.name), "assembled")
        self.log.add(self.event)

    def fetch_member_names(self) -> list:
        """
        Fetches the names of all members in the team.

        Returns:
            list: A list of member names.
        """
        member_names = [x.name for x in self.members]
        return member_names

    def request_introductions(self) -> None:
        """
        Requests introductions from all team members.
        """
        for member in self.members:
            member.outputs.add_message(f"Hello! My name is '{member.name}'")
            member.teammates = self.fetch_member_names()

    def fetch_updates(self) -> None:
        """
        Fetches updates from all team members.
        """
        for member in self.members:
            if len(member.inputs.history) > 0:
                self.inputs.history[member.name] = member.inputs.history
            if len(member.inputs.last.keys()) > 0:
                self.inputs.last[member.name] = member.inputs.last
            if len(member.outputs.history) > 0:
                self.outputs.history[member.name] = member.outputs.history
            if len(member.outputs.last.keys()) > 0:
                self.outputs.last[member.name] = member.outputs.last
            if member.final_answer and len(member.final_answer) > 0:
                self.final_answers[member.name] = member.final_answer

    def push_reviews(self) -> None:
        """
        Pushes reviews from reviewers to the respective members.
        """
        for member in self.members:
            if self.outputs.last:
                if self.outputs.last.get(f"{member.name}_reviewer", None):
                    reviewer_message = self.outputs.last.get(f"{member.name}_reviewer", None).get(
                        "message", None
                    )
                    if "Hello! I'm on team" not in reviewer_message:
                        member.inputs.add_message(reviewer_message)

    def return_self(self) -> "Team":
        """
        Returns the current instance of the team.

        Returns:
            Team: The current instance of the team.
        """
        return self

    def push_team_updates(self) -> None:
        """
        Pushes the current team instance to all members.
        """
        for member in self.members:
            member.team = self.return_self()

    def update(self) -> None:
        """
        Updates the team by fetching updates, pushing reviews, and pushing team updates.
        """
        self.fetch_updates()
        self.push_reviews()
        self.push_team_updates()

    def __call__(self, *args, **kwargs) -> dict:
        """
        Calls the update method and returns the current team instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: A dictionary containing the current team instance.
        """
        for arg in args:
            pass
        for kwarg in kwargs:
            pass
        self.update()
        return {"team": self.return_self()}


###################################################################################################
### Graph Classes
#### This module contains the functions used to create graphs that coordinate multi-agent workflows.


def create_team_graph(team: Team) -> StateGraph:
    """Creates a state graph for a given team.

    Args:
        team (Team): The team for which the state graph is created.

    Returns:
        StateGraph: The state graph representing the team's workflow.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")

        team_graph = StateGraph(team)

        # Add entry and exit nodes
        team_graph.set_entry_point(team.config.graph_config["entry"])
        if AGENTS[team.config.graph_config["finish"]]["needs_review"]:
            team_graph.set_finish_point(f"{team.config.graph_config['finish']}_reviewer")
        else:
            team_graph.set_finish_point(team.config.graph_config["finish"])

        # Add each agent on the team as a node
        for member in team.members:
            team_graph.add_node(
                member.name,
                member.invoke,
            )

        # Get pre-defined workflow order from config
        edge_order = team.config.graph_config["edge_order"]

        for edge_idx, member_name in enumerate(edge_order):
            if edge_idx < len(edge_order) - 1:
                next_member = edge_order[edge_idx + 1]
            else:
                next_member = END

            # Define the runnable that is used to see if an agent is finished
            @chain
            def check_member_finished(member_name=member_name):
                if member_name in team.members_finished:
                    return str(True)
                else:
                    return str(False)

            if AGENTS[member_name]["needs_review"]:
                team_graph.add_conditional_edges(
                    member_name,
                    check_member_finished,
                    {"True": next_member, "False": f"{member_name}_reviewer"},
                )
                if f"{member_name}_reviewer" != f'{team.config.graph_config["finish"]}_reviewer':
                    team_graph.add_edge(f"{member_name}_reviewer", next_member)
                else:
                    pass
            else:
                team_graph.add_edge(member_name, next_member)

    return team_graph


def compile_workflow(graph: StateGraph) -> dict:
    """Compiles the workflow from the given state graph.

    Args:
        graph (StateGraph): The state graph to compile.

    Returns:
        dict: The compiled workflow.
    """
    workflow = graph.compile()
    return workflow


def run_team_workflow(
    project_type: str = "small", project_goal: str = "Tell a funny dad joke", **kwargs
) -> Team:
    """Runs the team workflow for a given project type and goal.

    Args:
        project_type (str, optional): The type of the project. Defaults to "small".
        project_goal (str, optional): The goal of the project. Defaults to "Tell a funny dad joke".
        **kwargs: Additional keyword arguments.

    Returns:
        Team: The team after running the workflow.
    """
    project = Project(project_type, goal=project_goal)

    # TODO: implement project-level workflows with multiple teams

    # This selects the first team from a list of teams
    team = project.teams[0]
    team.goal = project_goal
    team_graph = create_team_graph(team)
    team_workflow = team_graph.compile()

    member_names = team.fetch_member_names()
    color_map = map_member_colors(member_names, color_names)

    prior_submissions = []
    for s in team_workflow.stream(team):
        if "__end__" not in s:
            for agent in team.fetch_member_names():
                try:
                    if "Hello! I'm on team" not in team.outputs.last[agent]["message"]:
                        if team.outputs.last[agent]["message"] not in prior_submissions:
                            print_heading(colored(agent, color=color_map[agent]))
                            try:
                                print_dict(
                                    team.outputs.last[agent]["message"],
                                    color=color_map[agent],
                                )
                            except:
                                print(
                                    colored(
                                        team.outputs.last[agent]["message"],
                                        color=color_map[agent],
                                    )
                                )
                            prior_submissions.append(team.outputs.last[agent]["message"])

                except Exception as e:
                    print(
                        "---------------------------------------------------------------------------------\n"
                    )
                    print(colored(f"An Exception occurred: {e}", "red", attrs=["bold"]))
                    print(
                        "---------------------------------------------------------------------------------\n"
                    )

    return team


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

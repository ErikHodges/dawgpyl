"""This module contains the Agent class, used in single-agent and multi-agent workflows."""

import json
from dataclasses import dataclass

from configs.agents import AGENTS
from configs.prompts import PROMPTS
from configs.tasks import TASKS
from libs.base import Event, Log, MessageLog, Target, Timestamp
from libs.common import get_class, parse_agent_response, eprint,print_dict, print_heading
from libs.io import read_file, write_file
from libs.models import Model
from libs.tasks import Task
from termcolor import colored
from langsmith import traceable


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
#TODO: Make sure I'm not overwriting the project state at this point
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

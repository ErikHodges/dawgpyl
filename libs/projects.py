"""This module contains the Project class, used to store the state of multiple multi-agent workflows."""

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


#     return tool_description

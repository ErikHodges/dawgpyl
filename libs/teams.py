"""This module contains the Team class, used to store the state of multi-agent workflows."""

import datetime as dt
import os
from dataclasses import dataclass
from uuid import uuid4
from typing import Annotated, Sequence, TypedDict

import pandas as pd
from configs.agents import AGENTS
from configs.core import DEFAULT_SEED
from configs.models import MODELS
from configs.prompts import PROMPTS
from configs.tasks import TASKS
from configs.teams import TEAMS
from libs.agents import Agent
from libs.base import Event, GroupMessageLog, Log, MessageLog, Target
from libs.common import generate_random_name, get_class
from libs.models import Model
from libs.tasks import Task


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
    inputs: GroupMessageLog | None
    outputs: GroupMessageLog | None
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
        self.inputs = GroupMessageLog()
        self.outputs = GroupMessageLog()
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
        self.event = Event(
            Target(get_class(self), self.name), f"added Agent('{agent2add}')"
        )
        self.log.add(self.event)

    def add_reviewer(self, agent2review: str) -> None:
        """
        Adds a reviewer to the team.

        Args:
            agent2review (str): The name of the agent to review.
        """
        reviewer_name = f"{agent2review}_reviewer"
        self.members.append(Agent(name=reviewer_name, agent_config="reviewer"))
        self.event = Event(
            Target(get_class(self), self.name), f"added Agent('{reviewer_name}')"
        )
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
                    reviewer_message = self.outputs.last.get(
                        f"{member.name}_reviewer", None
                    ).get("message", None)
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

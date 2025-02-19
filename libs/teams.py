"""This module contains the Team class, used to store the state of multi-agent workflows."""

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
### Team Classes


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

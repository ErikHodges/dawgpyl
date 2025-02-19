"""This module contains the functions used to create graphs that coordinate multi-agent workflows"""

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

"""This module contains the functions used to create graphs that coordinate multi-agent workflows."""

import warnings

from configs.agents import AGENTS
from langchain_core.runnables import chain
from langgraph.graph import END, StateGraph
from libs.common import color_names, map_member_colors, print_dict, print_heading
from libs.projects import Project
from libs.teams import Team
from termcolor import colored
import streamlit as st
from libs.io import read_file, write_file
from libs.base import Timestamp


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
            team_graph.set_finish_point(
                f"{team.config.graph_config['finish']}_reviewer"
            )
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
                if (
                    f"{member_name}_reviewer"
                    != f'{team.config.graph_config["finish"]}_reviewer'
                ):
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
                            prior_submissions.append(
                                team.outputs.last[agent]["message"]
                            )

                except Exception as e:
                    print(
                        "---------------------------------------------------------------------------------\n"
                    )
                    print(colored(f"An Exception occurred: {e}", "red", attrs=["bold"]))
                    print(
                        "---------------------------------------------------------------------------------\n"
                    )

    return team

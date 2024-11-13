from configs.agents import AGENTS
from configs.core import DEFAULT_SEED
from configs.models import DEFAULT_EMBEDDER, DEFAULT_LLM
from configs.prompts import PROMPTS
from libs.agents import Agent

TEAMS = {
    "small": {
        "leader": "director",
        "members": [
            "prompt_engineer",
            "responder",
            # "team_reporter",
        ],
        "graph_config": {
            "entry": "prompt_engineer",
            "finish": "responder",
            "edge_order": ["prompt_engineer", "responder"],
            "edges": [
                # ("prompt_engineer", "prompt_engineer_reviewer"),
                # ("prompt_engineer_reviewer", "responder"),
                # ("responder", "responder_reviewer"),
                ## ("responder_reviewer", "team_reporter"),
                ## ("team_reporter", "team_reporter_reviewer"),
            ],
        },
    },
    "generic": {
        "leader": "director",
        "members": [
            "goal_engineer",
            "project_manager",
            # "prompt_engineer",
            "task_manager",
            "researcher",
            "reporter",
        ],
        "graph_config": {
            "entry": "goal_engineer",
            "finish": "reporter",
            "edges": [
                # (edge_start,edge_end,bool(conditional))
                ("goal_engineer", "goal_engineer_reviewer"),
                ("goal_engineer_reviewer", "goal_engineer"),
                ("goal_engineer", "project_manager"),
                ("project_manager", "project_manager_reviewer"),
                ("project_manager_reviewer", "project_manager"),
                ("project_manager", "task_manager"),
                ("task_manager", "researcher"),
                ("researcher", "researcher_reviewer"),
                ("researcher_reviewer", "researcher"),
                ("researcher", "reporter"),
                ("reporter", "reporter_reviewer"),
                ("reporter_reviewer", "reporter"),
                ("reporter", "__end__"),
            ],
        },
    },
    "research": {
        "leader": "director",
        "members": [
            "director",
            "prompt_engineer",
            "task_decomposer",
            "prompt_engineer",
            "planner",
            "source_selector",
            "researcher",
            "reviewer",
        ],
        "graph_config": {
            "entry": "prompt_engineer",
            "finish": "default",
            "edges": [
                # (edge_start,edge_end,bool(conditional))
                ("default", "default", False),
            ],
        },
    },
    "default": {
        "leader": "task_manager",
        "members": [
            "task_manager",
            "director",
            "default",
        ],
        "graph_config": {
            "entry": "task_manager",
            "finish": "default.final_answer",
            "edges": [
                # (edge_start,edge_end,bool(conditional))
                ("default", "default", False),
            ],
        },
    },
    "default_research": {
        "leader": "task_manager",
        "members": [
            "task_manager",
            "director",
            "prompt_engineer",
            "researcher",
            "reviewer",
        ],
        "graph_config": {
            "entry": "prompt_engineer",
            "finish": "default",
            "edges": [
                # (edge_start,edge_end,bool(conditional))
                ("prompt_engineer", "researcher", False),
            ],
        },
    },
    "default_complex": {
        "leader": "director",
        "members": [
            "director",
            "acceptance_criteria_engineer",
            "task_decomposer",
        ],
        "graph_config": {
            "entry": "default",
            "finish": "default",
            "edges": [
                # (edge_start,edge_end,bool(conditional))
                ("default", "default", False),
            ],
        },
    },
}

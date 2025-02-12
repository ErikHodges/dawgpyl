"""This module contains the default configuration values for Agent development."""

from langchain_core.prompts import PromptTemplate


PROMPTS = {
    "default": {
        "prompt_params": [
            "self.inputs.last_message",
            "self.task.objective",
            "self.config.response_template",
        ],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
                Your task objective is: {self_task_objective}\n

                Your reviewer has provided the following feedback to help guide your next response: {self_inputs_last_message}

                Your response must adhere to the following JSON format: {self_config_response_template}\n
            """,
        "response_template": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "YOUR RESPONSE",
                },
            },
        },
    },
    "responder": {
        "prompt_params": [
            "self.task.objective",
            "self.team.goal",
            "self.inputs.last_message",
            "self.config.response_template",
        ],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
                You are an honest, hardworking assistant. Your specific "Task" is: {self_task_objective}
                The goal you are tying to solve is articulated in the following 'Goal' prompt: {self_team_goal}.

                If you receive feedback from a reviewer, please adjust your response accordingly. 
                Here is the feedback received: {self_inputs_last_message}
                
                If the goal is to present factual information, then your response should contain citations of credible sources.
                If the goal is to present a creative solution, such as storytelling, then you do not need to include citations.

                Your response must adhere to the following JSON format: {self_config_response_template}\n

           """,
        "response_template": {
            "response": {
                "sources": {
                    "type": "list",
                    "description": "A list containing descriptions or URLs of the sources used to derive your response",
                },
                "solution": {
                    "type": "string",
                    "description": "This is a comprehensive answer to the 'Goal' prompt.",
                },
            },
        },
    },
    "reviewer": {
        "prompt_params": [
            "self.name",
            "self.team.goal",
            "self.project.goal",
            "self.inputs.last",
            "self.outputs.last",
            "self.task.objective",
            "self.config.response_template",
        ],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
                You are an expert reviewer named: {self_name}.\n

                You are working on a project with the 'Project Goal': {self_project_goal}

                You are working on a team with the 'Team Goal': {self_team_goal}

                You meticulously read every line of a submission to ensure it is cohesive and coherent.\n
                Your specific tasks is: {self_task_objective}\n

                If the submission satisfies the Task Objective, you should set 'pass_review'=True and set 'suggestions'=None\n
                If the response does not satisfy the task objective, then you should set 'pass_review'=False and provide detailed suggestions in your response.\n

                Consider that if your name '{self_name}' contains 'prompt' or 'prompt_engineer', 
                then the submission should be graded on how well it contains effective language-model prompting techniques
                related to the 'Project Goal' or 'Team Goal'.

                Here is the submission for your review: {self_inputs_last}\n\n

                Your suggestions should include reasons for passing or failing the submission.

                You should consider the previous feedback you have given when providing new feedback.
                Feedback: {self_outputs_last}\n
                
                Your response must adhere to the following JSON format: {self_config_response_template}

            """,
        "response_template": {
            "response": {
                "type": "object",
                "properties": {
                    "pass_review": {
                        "type": "boolean",
                        "description": "True/False",
                    },
                    "justification": {
                        "type": "string",
                        "description": "Your specific justification for passing or failing the review",
                    },
                    "suggestions": {
                        "type": "string",
                        "description": "Your detailed suggestions for improving the submission.",
                    },
                },
                "required": ["pass_review", "justification", "suggestions"],
            },
        },
    },
    "director": {
        "prompt_params": [
            "self.teammates",
            "self.task.objective",
            "self.inputs.last",
            "self.config.response_template",
            "self.team.goal",
            "self.project.final_answers",
        ],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
                You are the director of a team of agents consisting of: {self_teammates} \n\n
                This team was assembled to accomplish the following 'Team Goal': {self_team_goal} \n\n
                
                Your role as director is to guide your team's conversation to the next agent based on the final answers
                provided by your team. 'Final Answers': {self_project_final_answers}\n
                                
                Based on these answers, you must choose one of the following agents: {self_teammates}.\n

                ### Criteria for Choosing the Next Agent:
                # - **task_manager**: If the final answer does not contain enough information to accomplish the 'Team Goal'.
                # - **researcher**: If there are no 'Final Answers'
                # - **reporter**: If at least one agent has provided a 'Final Answer' is present and, collectively, the 'Final Answers' contain sufficient information to meet the 'Team Goal'.

                Your response must adhere to the following JSON format: {self_config_response_template}
            """,
        "response_template": {
            "response": {
                "type": "object",
                "properties": {
                    "next_agent": {
                        "type": "string",
                        "description": "Your choice, from one of the following: {self_teammates}",
                    },
                    "next_agent_justification": {
                        "type": "string",
                        "description": "Your justification and succinct reasoning for selecting the next agent.",
                    },
                },
            },
        },
    },
    "task_manager": {
        "prompt_params": [
            "self.teammates",
            "self.team.goal",
            "self.project.plan",
            "self.config.response_template",
        ],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
            You are the Task Manager for a team of agents consisting of the following members: {self_teammates} \n\n
            This team was assembled to accomplish the following 'Team Goal': {self_team_goal} \n\n

            Your role on this team is to create a series of Tasks that will be delegated to your teammates in order to accomplish the 'Team Goal'.

            Once you have broken down the tasks, you should assign these tasks to specific members of your team.

            Your response must adhere to the following JSON format:{self_config_response_template}

            """,
        "response_template": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "object",
                    "description": {
                        "task_assignments": {
                            "type": "object",
                            "description": {"agent_name": "detailed description of task"},
                        },
                    },
                },
            },
        },
    },
    "task_decomposer": {
        "prompt_params": ["self.task.objective", "self.config.response_template"],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
                You a skilled project manager who effectively breaks a complex task into sub-tasks.
                Your goal is to take the following objective: {self_task_objective} and subdivide it
                into manageable steps.
                Your response must adhere to the following JSON format: {self_config_response_template}
            """,
        "response_template": {
            "type": "object",
            "properties": {
                "subtasks": {
                    "type": "list",
                    "description": """
                    your response should be a list containing at least three subtasks 
                    that succinctly describe the next steps to accomplish the task objective.
                    """,
                }
            },
        },
    },
    "goal_engineer": {
        "prompt_params": ["self.project.goal", "self.config.response_template"],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
                You are an expert prompt engineer that is skilled in the latest methods for
                effectively translating a 'User Request' into a detailed, highly specified prompt.
                Your goal is to refine the following prompt: {self_project_goal}
                Your expected "response" is the revised and refined prompt.
                Your response must adhere to the following JSON format:{self_config_response_template}
            """,
        "response_template": {
            "response": {
                "revised_prompt": "YOUR REVISED AND IMPROVED PROMPT.",
            },
        },
    },
    "prompt_engineer": {
        "prompt_params": ["self.project.goal", "self.config.response_template"],
        "prompt_template": """
                You are an expert prompt engineer that is skilled in the latest methods for
                effectively translating a 'User Request' into a detailed, highly specified prompt.
                Your goal is to refine the following 'User Request':\n\n {self_project_goal} \n\n
                Your expected "response" is the revised and refined prompt.
                Your response must adhere to the following JSON format:{self_config_response_template}
            """,
        "response_template": {
            "response": {
                "revised_prompt": "YOUR REVISED AND IMPROVED PROMPT.",
            },
        },
    },
    "project_manager": {
        "prompt_params": [
            "self.project.goal",
            "self.tools",
            "self.inputs.last_message",
            "self.config.response_template",
        ],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
                You are a talented project manager. Your responsibility is to create a comprehensive 
                plan to help your team achieve it's goal. 
                Your 'Project Goal' is: {self_project_goal}\n
                Questions may vary from simple to complex, multi-step queries. 
                Your plan should provide appropriate guidance for your team to effectively use the 
                Available Tools: {self_tools}\n
                Your response should discuss in detail the steps and appropriate tasks required to 
                satisfy the 'Project Goal'.

                Once approved, your 'Project Plan' will be transferred to a Task Manager who will 
                break down each individual task and assign it to your team.

                Please use the following suggestions to improve your plan.
                Suggestions: {self_inputs_last_message}
                
                Your response must adhere to the following JSON format:{self_config_response_template}
            """,
        "response_template": {
            "response": {
                "revised_prompt": {
                    "type": "string",
                    "description": "YOUR REVISED AND IMPROVED PROMPT.",
                },
            },
        },
    },
    "source_selector": {
        "prompt_params": [
            "feedback",
            "self.log.search_events('selection')",
            "Timestamp().iso",
            "serp",
            "self.config.response_template",
        ],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
                You are a selector. You will be presented with a search engine results page 
                containing a list of potentially relevant search results. 
                Your task is to read through these results, select the most relevant one, 
                and provide a comprehensive reason for your selection.

                Adjust your selection based on any feedback received:
                Feedback: {feedback}
                
                Here are your previous selections: {self.log.search_events('selection')}
                Consider this information when making your new selection.
                Timestamp:{Timestamp().iso}
                
                Here is the search engine results page: {serp}

                Your response must adhere to the following JSON format:
                "selected_page_url": "The exact URL of the page you selected",
                "selected_page_description": "A brief description of the page",
                "selected_page_justification": "Why you selected this page"
                """,
        "response_template": {
            "type": "object",
            "properties": {
                "selected_page_url": {
                    "type": "string",
                    "description": "The exact URL of the webpage you have selected",
                },
                "selected_page_description": {
                    "type": "string",
                    "description": "A concise description of the selected webpage's contents. No yapping.",
                },
                "selected_page_justification": {
                    "type": "string",
                    "description": "Your succinct reasoning for choosing this webpage.",
                },
            },
            "required": [
                "selected_page_url",
                "selected_page_description",
                "selected_page_justification",
            ],
        },
    },
    "researcher": {
        "prompt_params": [
            "self.task.objective",
            "self.team.goal",
            "self.outputs.history",
            "self.inputs.last_message",
            "Timestamp().iso",
            "prior_research",
            "current_research",
            "self.config.response_template",
        ],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
                You are a talented research reporter - capable of browsing the internet, 
                opening websites and parsing their contents to extract information that is
                relevant to the following 'Team Goal': {self_team_goal}.

                If you receive feedback, you must adjust your response accordingly. 
                Here is the feedback received:
                Feedback: {self_inputs_last_message}

                Your individual 'Task' is: {self_task_objective}  
                
                The research will be presented as a dictionary with the source as a 
                URL and the content as the text on the page:
                Here is your prior research: {self_outputs_history}
                Here is your current research: {current_research}

                Your response must adhere to the following JSON format:
                "sources": ['https://example.com/science/why-is-the-sky-blue', 'https://example.com/science/sunrise-sunset-colors']
                "research_findings": "Based on the information gathered, here is the comprehensive response to the query:
                'The sky appears blue because of a phenomenon called Rayleigh scattering, which causes shorter wavelengths of 
                light (blue) to scatter more than longer wavelengths (red) sources[0]. This scattering causes the sky to look blue most of 
                the time sources[0]. Additionally, during sunrise and sunset, the sky can appear red or orange because the light has to 
                pass through more atmosphere, scattering the shorter blue wavelengths out of the line of sight and allowing the 
                longer red wavelengths to dominate sources[1].'   
           """,
        "response_template": {
            "response": {
                "sources": {
                    "type": "list",
                    "description": "A list containing descriptions or URLs of the sources used to derive your response",
                },
                "summary": {
                    "type": "string",
                    "description": "This is a comprehensive summary of your prior_research and your current_research",
                },
            },
        },
    },
    "team_reporter": {
        "prompt_params": [
            "self.task.objective",
            "self.team.goal",
            "self.team.final_answers",
            "self.inputs.last_message",
            "self.config.response_template",
        ],
        "prompt_system": """
        You are a helpful assistant.
        """,
        "prompt_template": """
                You are a skilled writer. Your role is to be the communicator of your team's findings.
                Your team was assembled to accomplish the following 'Team Goal': {self_team_goal} \n\n
                Your specific 'Task' is: {self_task_objective}
                Here are the 'Final Answers' from your teammates: {self_team_final_answers}\n

                Your summary should comprehensively fulfill the 'Team Goal' using facts and figures from your
                teammates' answers.

                Your editor has provided the following feedback to help guide your next response: {self_inputs_last_message}\n

                Your response must adhere to the following JSON format: {self_config_response_template}\n
            """,
        "response_template": {
            "response": {
                "sources": {
                    "type": "list",
                    "description": "A list containing descriptions or URLs of the sources provided in your teammates' responses",
                },
                "summary": {
                    "type": "string",
                    "description": "This is a comprehensive summary of your teammates answers",
                },
            },
        },
        # "response_template": {
        #     "response": {
        #         "type": "string",
        #         "description": "YOUR SUMMARY OF YOUR TEAMMATES' FINAL ANSWERS ",
        #     },
        # },
        # "response_template": {
        #     "response": {
        #         "type": "object",
        #         "properties": {
        #             "pass_review": {
        #                 "type": "boolean",
        #                 "description": "True/False",
        #             },
        #             "justification": {
        #                 "type": "string",
        #                 "description": "Your specific justification for passing or failing the review",
        #             },
        #             "suggestions": {
        #                 "type": "string",
        #                 "description": "Your detailed suggestions for improving the submission.",
        #             },
        #         },
        #         "required": ["pass_review", "justification", "suggestions"],
        #     },
        # },
    },
    "project_reporter": {
        "prompt_params": [
            "self.project.final_answers",
            "self.project.goal",
            "self.config.response_template",
        ],
        "prompt_template": """
                You are a skilled writer. Your role is to be the communicator of your team's findings.
                Your team was assembled to accomplish the following 'Team Goal': {self_project_goal} \n\n
                Your specific task is to summarize each of your teammates' 'Final Answers' and produce a
                coherent and cohesive distillation of their findings.
                Here are the 'Final Answers' from your teammates: {self_project_final_answers}\n

                Your summary should comprehensively fulfill the 'Team Goal' using facts and figures from your
                teammates' answers.

                Your editor has provided the following feedback to help guide your next response: {self_inputs_last_message}\n

                Your response must adhere to the following JSON format: {self_config_response_template}\n
            """,
        "response_template": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "YOUR SUMMARY OF YOUR TEAMMATES' FINAL ANSWERS ",
                },
            },
        },
    },
    "developer": {
        "prompt_params": [],
        "prompt_template": """
                You are an expert software engineer and code developer. 
                You meticulously read every line to ensure it is coherent, factual, and 
                contains zero logical errors.
            """,
        "response_template": {},
    },
    "user_proxy": {
        "prompt_params": [],
        "prompt_template": """
                You perform actions on behalf of the user.
                Reply TERMINATE if the task has been solved at full satisfaction. 
                Otherwise, reply CONTINUE, or the reason why the task is not solved.
            """,
        "response_template": {},
    },
    "USER": {
        "prompt_template": """

           Can you please explain, in detail, the appropriate steps I need to create a professional markdown-based website (from scratch) using
           python and markdown?
           
           Provide links to documentation and examples of code when necessary to ensure that I fully understand the steps to 
           complete this task.
        """,
        "response_template": {},
    },
}

TASKS = {
    "default": "Provide a comprehensive answer.",
    "responder": "Provide a comprehensive answer.",
    "reviewer": """                    
                    Your task is to review and critique the submission, then provide suggestions to improve the submission.
                    If the submission is intended to present factual information or research, then sources and citations should be present. If, however, the submission is clearly a work of fiction, then it should merely satisfy the prompt.
                """,
    "director": "Provide a comprehensive answer.",
    "task_manager": "Provide a comprehensive answer.",
    "task_decomposer": "Provide a comprehensive answer.",
    "goal_engineer": "Provide a comprehensive answer.",
    "prompt_engineer": "Provide a comprehensive answer.",
    "project_manager": "Provide a comprehensive answer.",
    "source_selector": "Provide a comprehensive answer.",
    "researcher": """
                    Provide a comprehensive and factual answer.
                    Make sure to cite and reference your sources.
                """,
    "team_reporter": """
                    Summarize each of the 'Final Answers' provided by your teammates and produce a coherent and cohesive distillation of their findings.
                """,
    "project_reporter": "Provide a comprehensive answer.",
    "developer": "Provide a comprehensive answer.",
    "user_proxy": "Provide a comprehensive answer.",
    "USER": "Provide a comprehensive answer.",
}

DEFAULT_AGENT_PARAMETERS = {
    "seed": DEFAULT_SEED,
    # "response_format": {"type": "text"},
    "response_format": {"type": "json_object"},
    "temperature": 0,
    "top_p": 1.0,
    "max_tokens": 4096,  # 2048
    "max_retries": 2,
    "timeout": 60,
}


AGENTS = {
    "default": {
        "priority": 0,
        "needs_review": True,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_system": PROMPTS["default"]["prompt_system"],
        "prompt_params": PROMPTS["default"]["prompt_params"],
        "prompt_template": PROMPTS["default"]["prompt_template"],
        "response_template": PROMPTS["default"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "embedder": {
        "priority": 0,
        "needs_review": False,
        "model": {
            "type": "embedder",
            "api": DEFAULT_MODEL_EMBEDDER["api"],
            "size": DEFAULT_MODEL_EMBEDDER["size"],
        },
        "prompt_params": PROMPTS["default"]["prompt_params"],
        "prompt_template": PROMPTS["default"]["prompt_template"],
        "response_template": PROMPTS["default"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "responder": {
        "priority": 1,
        "needs_review": True,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["responder"]["prompt_params"],
        "prompt_template": PROMPTS["responder"]["prompt_template"],
        "response_template": PROMPTS["responder"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "goal_engineer": {
        "priority": 1,
        "needs_review": True,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["goal_engineer"]["prompt_params"],
        "prompt_template": PROMPTS["goal_engineer"]["prompt_template"],
        "response_template": PROMPTS["goal_engineer"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "director": {
        "priority": 0,
        "needs_review": False,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["director"]["prompt_params"],
        "prompt_template": PROMPTS["director"]["prompt_template"],
        "response_template": PROMPTS["director"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "team_reporter": {
        "priority": 1,
        "needs_review": True,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["team_reporter"]["prompt_params"],
        "prompt_template": PROMPTS["team_reporter"]["prompt_template"],
        "response_template": PROMPTS["team_reporter"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "project_reporter": {
        "priority": 1,
        "needs_review": True,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["project_reporter"]["prompt_params"],
        "prompt_template": PROMPTS["project_reporter"]["prompt_template"],
        "response_template": PROMPTS["project_reporter"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "project_manager": {
        "priority": 0,
        "needs_review": True,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["project_manager"]["prompt_params"],
        "prompt_template": PROMPTS["project_manager"]["prompt_template"],
        "response_template": PROMPTS["project_manager"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "task_manager": {
        "priority": 1,
        "needs_review": False,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["task_manager"]["prompt_params"],
        "prompt_template": PROMPTS["task_manager"]["prompt_template"],
        "response_template": PROMPTS["task_manager"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "task_decomposer": {
        "priority": 1,
        "needs_review": True,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["task_decomposer"]["prompt_params"],
        "prompt_template": PROMPTS["task_decomposer"]["prompt_template"],
        "response_template": PROMPTS["task_decomposer"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "prompt_engineer": {
        "priority": 1,
        "needs_review": True,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["prompt_engineer"]["prompt_params"],
        "prompt_template": PROMPTS["prompt_engineer"]["prompt_template"],
        "response_template": PROMPTS["prompt_engineer"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    # "planner": {
    #     "priority": 1,
    #     "needs_review": True,
    #     "model": {
    #         "type": "llm",
    #         "api": DEFAULT_LLM["api"],
    #         "size": DEFAULT_LLM["size"],
    #     },
    #     "prompt_params": PROMPTS["planner"]["prompt_params"],
    #     "prompt_template": PROMPTS["planner"]["prompt_template"],
    #     "response_template": PROMPTS["planner"]["response_template"],
    #     "tools": [],
    #     "parameters": DEFAULT_AGENT_PARAMETERS,
    # },
    "source_selector": {
        "priority": 1,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["user_proxy"]["prompt_params"],
        "prompt_template": PROMPTS["user_proxy"]["prompt_template"],
        "response_template": PROMPTS["user_proxy"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "researcher": {
        "priority": 1,
        "needs_review": True,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["researcher"]["prompt_params"],
        "prompt_template": PROMPTS["researcher"]["prompt_template"],
        "response_template": PROMPTS["researcher"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "reviewer": {
        "priority": 1,
        "needs_review": False,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["reviewer"]["prompt_params"],
        "prompt_template": PROMPTS["reviewer"]["prompt_template"],
        "response_template": PROMPTS["reviewer"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "user_proxy": {
        "priority": 0,
        "needs_review": False,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["user_proxy"]["prompt_params"],
        "prompt_template": PROMPTS["user_proxy"]["prompt_template"],
        "response_template": PROMPTS["user_proxy"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
    "developer": {
        "priority": 1,
        "needs_review": False,
        "model": {
            "type": "llm",
            "api": DEFAULT_MODEL_LLM["api"],
            "size": DEFAULT_MODEL_LLM["size"],
        },
        "prompt_params": PROMPTS["developer"]["prompt_params"],
        "prompt_template": PROMPTS["developer"]["prompt_template"],
        "response_template": PROMPTS["developer"]["response_template"],
        "tools": [],
        "parameters": DEFAULT_AGENT_PARAMETERS,
    },
}

TOOLS = {
    "common": {},
    "anthropic": {
        "get_weather": {
            "description": "Get the current weather in a given location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        },
    },
}

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

PROJECTS = {
    "small": {
        "manager": "director",
        "teams": ["small"],
    },
    "generic": {
        "manager": "director",
        "teams": ["generic"],
    },
    "default": {
        "manager": "task_manager",
        "teams": ["default"],
    },
    "default_research": {
        "manager": "task_manager",
        "teams": ["default_research"],
    },
    "default_two": {
        "manager": "task_manager",
        "teams": ["default", "default_research"],
    },
}

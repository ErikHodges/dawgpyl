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
from libs.base import Event, Log, Target
from libs.common import get_class


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
        self.event = Event(
            Target(get_class(self), self.name), f"assignee changed: {self.assignee}"
        )
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

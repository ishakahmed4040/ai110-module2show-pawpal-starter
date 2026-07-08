"""PawPal+ logic layer.

Class stubs generated from diagrams/uml.mmd. No scheduling logic yet —
fill in method bodies incrementally.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    recurrence: str = "once"
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def conflicts_with(self, other: "Task") -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id) -> None:
        pass

    def edit_task(self, task_id, updates: dict) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_pets(self) -> List[Pet]:
        pass


class Scheduler:
    def __init__(self, available_time: int):
        self.available_time = available_time

    def generate_plan(self, tasks: List[Task]) -> List[Task]:
        pass

    def explain_plan(self) -> str:
        pass

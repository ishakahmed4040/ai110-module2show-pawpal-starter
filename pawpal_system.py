"""PawPal+ logic layer.

Core classes for the pet care scheduling system, built from diagrams/uml.mmd.
"""

import itertools
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import ClassVar, Dict, List, Optional

_id_counter = itertools.count(1)


def _parse_time(value: str) -> int:
    """Convert an 'HH:MM' string to minutes since midnight."""
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


def _format_time(minutes: int) -> str:
    """Convert minutes since midnight back to an 'HH:MM' string."""
    hours, mins = divmod(minutes % (24 * 60), 60)
    return f"{hours:02d}:{mins:02d}"


@dataclass
class Task:
    name: str
    duration: int  # minutes
    priority: str = "medium"  # "high" | "medium" | "low"
    recurrence: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False
    preferred_time: Optional[str] = None  # "HH:MM", or None if flexible
    due_date: date = field(default_factory=date.today)
    id: int = field(default_factory=lambda: next(_id_counter))

    _PRIORITY_RANK: ClassVar[Dict[str, int]] = {"high": 0, "medium": 1, "low": 2}
    _RECURRENCE_DELTA: ClassVar[Dict[str, timedelta]] = {
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
    }

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """If this task recurs (daily/weekly), return a new Task instance due on the next date."""
        delta = self._RECURRENCE_DELTA.get(self.recurrence)
        if delta is None:
            return None
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            recurrence=self.recurrence,
            completed=False,
            preferred_time=self.preferred_time,
            due_date=self.due_date + delta,
        )

    def conflicts_with(self, other: "Task") -> bool:
        """Two tasks conflict only if both have a preferred time and those windows overlap."""
        if not self.preferred_time or not other.preferred_time:
            return False
        self_start = _parse_time(self.preferred_time)
        self_end = self_start + self.duration
        other_start = _parse_time(other.preferred_time)
        other_end = other_start + other.duration
        return self_start < other_end and other_start < self_end


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove the task with the given id, if it exists."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def edit_task(self, task_id: int, updates: dict) -> None:
        """Apply a dict of attribute updates to the task with the given id."""
        for task in self.tasks:
            if task.id == task_id:
                for key, value in updates.items():
                    setattr(task, key, value)
                return

    def get_tasks(self) -> List[Task]:
        """Return this pet's list of tasks."""
        return self.tasks

    def mark_task_complete(self, task_id: int) -> Optional[Task]:
        """Complete the given task; if it recurs, add and return its next occurrence."""
        for task in self.tasks:
            if task.id == task_id:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task is not None:
                    self.add_task(next_task)
                return next_task
        return None


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return this owner's list of pets."""
        return self.pets

    def get_all_tasks(self) -> List[Task]:
        """Flatten tasks across every pet this owner has."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """Return all tasks across every pet matching the given completion status."""
        return [task for task in self.get_all_tasks() if task.completed == completed]

    def get_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Return the tasks belonging to the pet with the given name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet.get_tasks()
        return []


class Scheduler:
    """Retrieves tasks from an Owner's pets and builds a feasible daily plan."""

    def __init__(self, available_time: int, day_start: str = "08:00"):
        self.available_time = available_time
        self.day_start = day_start
        self.plan: List[dict] = []
        self.skipped: List[dict] = []

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted chronologically by preferred_time; tasks without one sort last."""
        return sorted(tasks, key=lambda task: task.preferred_time or "99:99")

    def find_conflicts(self, owner: Owner) -> List[str]:
        """Check every pair of the owner's pending tasks for overlapping preferred times.

        Lightweight by design: a simple O(n^2) pairwise scan over a small daily task list,
        returning plain warning strings instead of raising — callers decide how to surface them.
        """
        pet_by_task_id = {task.id: pet.name for pet in owner.get_pets() for task in pet.get_tasks()}
        tasks = [task for task in owner.get_all_tasks() if not task.completed]

        warnings = []
        for task_a, task_b in itertools.combinations(tasks, 2):
            if task_a.conflicts_with(task_b):
                pet_a = pet_by_task_id.get(task_a.id, "Unknown pet")
                pet_b = pet_by_task_id.get(task_b.id, "Unknown pet")
                warnings.append(
                    f"Conflict: '{task_a.name}' ({pet_a}, {task_a.preferred_time}) overlaps "
                    f"with '{task_b.name}' ({pet_b}, {task_b.preferred_time})"
                )
        return warnings

    def generate_plan(self, owner: Owner) -> List[dict]:
        """Build a prioritized daily plan from the owner's pets' tasks, within available_time."""
        today = date.today()
        tasks = [
            task
            for task in owner.get_all_tasks()
            if not task.completed and task.due_date <= today
        ]
        tasks.sort(
            key=lambda task: (
                Task._PRIORITY_RANK.get(task.priority, 1),
                task.preferred_time or "99:99",
            )
        )

        self.plan = []
        self.skipped = []
        time_used = 0
        cursor = _parse_time(self.day_start)

        for task in tasks:
            if time_used + task.duration > self.available_time:
                self.skipped.append({"task": task, "reason": "not enough time remaining"})
                continue

            conflict = any(task.conflicts_with(entry["task"]) for entry in self.plan)
            if conflict:
                self.skipped.append({"task": task, "reason": "conflicts with an already-scheduled task"})
                continue

            start_minutes = _parse_time(task.preferred_time) if task.preferred_time else cursor
            self.plan.append({"task": task, "start_time": _format_time(start_minutes)})
            time_used += task.duration
            cursor = max(cursor, start_minutes) + task.duration

        return self.plan

    def explain_plan(self) -> str:
        """Render the current plan (and any skipped tasks with reasons) as readable text."""
        if not self.plan and not self.skipped:
            return "No plan has been generated yet."

        lines = [
            f"{entry['start_time']} — {entry['task'].name} "
            f"({entry['task'].duration} min) [priority: {entry['task'].priority}]"
            for entry in self.plan
        ]

        if self.skipped:
            lines.append("")
            lines.append("Skipped:")
            lines.extend(f"- {entry['task'].name}: {entry['reason']}" for entry in self.skipped)

        return "\n".join(lines)

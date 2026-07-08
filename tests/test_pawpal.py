from datetime import date, timedelta

from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    task = Task(name="Morning walk", duration=30, priority="high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task(name="Feeding", duration=10, priority="high"))

    assert len(pet.get_tasks()) == 1


def test_completing_daily_task_spawns_next_occurrence():
    pet = Pet(name="Mochi", species="dog")
    today = date.today()
    task = Task(name="Give medication", duration=5, priority="high", recurrence="daily", due_date=today)
    pet.add_task(task)

    next_task = pet.mark_task_complete(task.id)

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)
    assert len(pet.get_tasks()) == 2


def test_completing_once_task_does_not_spawn_next_occurrence():
    pet = Pet(name="Mochi", species="dog")
    task = Task(name="Vet visit", duration=60, priority="high", recurrence="once")
    pet.add_task(task)

    next_task = pet.mark_task_complete(task.id)

    assert task.completed is True
    assert next_task is None
    assert len(pet.get_tasks()) == 1

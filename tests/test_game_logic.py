from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


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


def test_sort_by_time_returns_chronological_order():
    scheduler = Scheduler(available_time=120)
    early = Task(name="Feeding", duration=10, preferred_time="07:00")
    middle = Task(name="Morning walk", duration=30, preferred_time="08:00")
    late = Task(name="Evening walk", duration=20, preferred_time="18:00")
    flexible = Task(name="Litter box cleaning", duration=10)  # no preferred_time

    sorted_tasks = scheduler.sort_by_time([late, flexible, early, middle])

    assert [task.name for task in sorted_tasks] == [
        "Feeding",
        "Morning walk",
        "Evening walk",
        "Litter box cleaning",
    ]


def test_find_conflicts_flags_tasks_at_the_same_time():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(name="Morning walk", duration=30, preferred_time="08:00"))
    pet.add_task(Task(name="Vet checkup", duration=15, preferred_time="08:00"))
    owner.add_pet(pet)

    conflicts = Scheduler(available_time=120).find_conflicts(owner)

    assert len(conflicts) == 1
    assert "Morning walk" in conflicts[0]
    assert "Vet checkup" in conflicts[0]


def test_find_conflicts_ignores_back_to_back_tasks():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(name="Morning walk", duration=30, preferred_time="08:00"))
    pet.add_task(Task(name="Feeding", duration=10, preferred_time="08:30"))
    owner.add_pet(pet)

    conflicts = Scheduler(available_time=120).find_conflicts(owner)

    assert conflicts == []


def test_generate_plan_handles_pet_with_no_tasks():
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Ghost", species="hamster"))

    scheduler = Scheduler(available_time=60)
    plan = scheduler.generate_plan(owner)

    assert plan == []
    assert scheduler.skipped == []

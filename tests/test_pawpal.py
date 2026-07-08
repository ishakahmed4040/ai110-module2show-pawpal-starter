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

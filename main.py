"""Temporary testing ground for PawPal+ logic. Run with: python main.py"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo() -> Owner:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog")
    # Added out of chronological order on purpose, to prove sort_by_time actually sorts.
    mochi.add_task(Task(name="Evening walk", duration=20, priority="medium", preferred_time="18:00"))
    mochi.add_task(Task(name="Morning walk", duration=30, priority="high", preferred_time="08:00"))
    mochi.add_task(Task(name="Feeding", duration=10, priority="high", preferred_time="08:30"))
    mochi.add_task(
        Task(name="Give medication", duration=5, priority="high", preferred_time="09:00", recurrence="daily")
    )

    whiskers = Pet(name="Whiskers", species="cat")
    whiskers.add_task(Task(name="Playtime", duration=15, priority="low", preferred_time="17:00"))
    whiskers.add_task(Task(name="Feeding", duration=5, priority="high", preferred_time="07:45"))
    whiskers.add_task(Task(name="Litter box cleaning", duration=10, priority="medium"))
    # Deliberately overlaps Mochi's "Morning walk" (08:00-08:30) to demonstrate conflict detection.
    whiskers.add_task(Task(name="Vet checkup", duration=15, priority="high", preferred_time="08:00"))

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # Mark one task complete so status filtering has something to demonstrate.
    whiskers.get_tasks()[0].mark_complete()

    return owner


def print_schedule(owner: Owner, scheduler: Scheduler) -> None:
    pet_by_task_id = {task.id: pet.name for pet in owner.get_pets() for task in pet.get_tasks()}

    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)

    if not scheduler.plan:
        print("No tasks scheduled.")
    else:
        for entry in scheduler.plan:
            task = entry["task"]
            pet_name = pet_by_task_id.get(task.id, "Unknown pet")
            print(
                f"{entry['start_time']} — {task.name} ({pet_name}, {task.duration} min) "
                f"[priority: {task.priority}]"
            )

    if scheduler.skipped:
        print()
        print("Skipped:")
        for entry in scheduler.skipped:
            task = entry["task"]
            pet_name = pet_by_task_id.get(task.id, "Unknown pet")
            print(f"- {task.name} ({pet_name}): {entry['reason']}")


def print_tasks(label: str, tasks) -> None:
    print(label)
    print("-" * len(label))
    if not tasks:
        print("(none)")
    else:
        for task in tasks:
            time_str = task.preferred_time or "flexible"
            status = "done" if task.completed else "pending"
            print(f"{task.due_date} {time_str} — {task.name} [{task.priority}, {status}]")
    print()


def main() -> None:
    owner = build_demo()
    scheduler = Scheduler(available_time=60)

    conflicts = scheduler.find_conflicts(owner)
    print("Conflict check")
    print("=" * 40)
    if conflicts:
        for warning in conflicts:
            print(warning)
    else:
        print("No conflicts found.")
    print()

    scheduler.generate_plan(owner)
    print_schedule(owner, scheduler)

    print()
    print_tasks(
        "All tasks sorted by time",
        scheduler.sort_by_time(owner.get_all_tasks()),
    )
    print_tasks(
        "Incomplete tasks only",
        owner.get_tasks_by_status(completed=False),
    )
    print_tasks(
        "Completed tasks only",
        owner.get_tasks_by_status(completed=True),
    )
    print_tasks(
        "Whiskers' tasks only",
        owner.get_tasks_by_pet("Whiskers"),
    )

    print("Recurring task demo: completing Mochi's daily medication")
    print("=" * 55)
    mochi = next(pet for pet in owner.get_pets() if pet.name == "Mochi")
    medication = next(task for task in mochi.get_tasks() if task.name == "Give medication")
    mochi.mark_task_complete(medication.id)
    print_tasks("Mochi's tasks after marking medication complete", mochi.get_tasks())


if __name__ == "__main__":
    main()

"""Temporary testing ground for PawPal+ logic. Run with: python main.py"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo() -> Owner:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(Task(name="Morning walk", duration=30, priority="high", preferred_time="08:00"))
    mochi.add_task(Task(name="Feeding", duration=10, priority="high", preferred_time="08:30"))
    mochi.add_task(Task(name="Evening walk", duration=20, priority="medium", preferred_time="18:00"))

    whiskers = Pet(name="Whiskers", species="cat")
    whiskers.add_task(Task(name="Feeding", duration=5, priority="high"))
    whiskers.add_task(Task(name="Litter box cleaning", duration=10, priority="medium"))
    whiskers.add_task(Task(name="Playtime", duration=15, priority="low"))

    owner.add_pet(mochi)
    owner.add_pet(whiskers)
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


def main() -> None:
    owner = build_demo()
    scheduler = Scheduler(available_time=60)
    scheduler.generate_plan(owner)
    print_schedule(owner, scheduler)


if __name__ == "__main__":
    main()

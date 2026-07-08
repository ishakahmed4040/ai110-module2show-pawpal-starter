import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

owner = st.session_state.owner

available_time = st.number_input("Available time today (minutes)", min_value=15, max_value=600, value=90)
scheduler = Scheduler(available_time=int(available_time))

st.markdown("### Pets")

pet_col1, pet_col2 = st.columns(2)
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if any(pet.name == pet_name for pet in owner.get_pets()):
        st.info(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added {pet_name} ({species}).")

pets = owner.get_pets()
if pets:
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species, "tasks": len(p.get_tasks())} for p in pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed directly into the scheduler below.")

if pets:
    selected_pet_name = st.selectbox("Add task to which pet?", [p.name for p in pets])
else:
    selected_pet_name = None
    st.warning("Add a pet before adding tasks.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    has_fixed_time = st.checkbox("Set a specific time?")
    preferred_time = st.time_input("Preferred time", disabled=not has_fixed_time) if has_fixed_time else None
with col5:
    recurrence = st.selectbox("Repeats", ["once", "daily", "weekly"])

if st.button("Add task"):
    if selected_pet_name is None:
        st.warning("Add a pet before adding tasks.")
    else:
        target_pet = next(pet for pet in pets if pet.name == selected_pet_name)
        target_pet.add_task(
            Task(
                name=task_title,
                duration=int(duration),
                priority=priority,
                recurrence=recurrence,
                preferred_time=preferred_time.strftime("%H:%M") if preferred_time else None,
            )
        )
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

pet_by_task_id = {task.id: pet.name for pet in pets for task in pet.get_tasks()}

st.markdown("#### Task list")
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    status_filter = st.selectbox("Show", ["All", "Pending", "Completed"])
with filter_col2:
    pet_filter = st.selectbox("Pet", ["All pets"] + [p.name for p in pets])

filtered_tasks = owner.get_tasks_by_pet(pet_filter) if pet_filter != "All pets" else owner.get_all_tasks()
if status_filter == "Pending":
    filtered_tasks = [task for task in filtered_tasks if not task.completed]
elif status_filter == "Completed":
    filtered_tasks = [task for task in filtered_tasks if task.completed]

sorted_tasks = scheduler.sort_by_time(filtered_tasks)

if sorted_tasks:
    st.table(
        [
            {
                "time": task.preferred_time or "flexible",
                "task": task.name,
                "pet": pet_by_task_id.get(task.id, "Unknown pet"),
                "duration_minutes": task.duration,
                "priority": task.priority,
                "repeats": task.recurrence,
                "status": "done" if task.completed else "pending",
            }
            for task in sorted_tasks
        ]
    )
else:
    st.info("No tasks match this filter yet.")

pending_tasks = [task for task in owner.get_all_tasks() if not task.completed]
if pending_tasks:
    task_labels = {f"{pet_by_task_id.get(t.id, '?')} — {t.name}": t for t in pending_tasks}
    complete_label = st.selectbox("Mark a task complete", list(task_labels.keys()))
    if st.button("Mark complete"):
        task_to_complete = task_labels[complete_label]
        owning_pet = next(pet for pet in pets if task_to_complete in pet.get_tasks())
        next_task = owning_pet.mark_task_complete(task_to_complete.id)
        if next_task is not None:
            st.success(f"Completed '{task_to_complete.name}'. Next occurrence added for {next_task.due_date}.")
        else:
            st.success(f"Completed '{task_to_complete.name}'.")

conflicts = scheduler.find_conflicts(owner)
if conflicts:
    st.markdown("#### ⚠️ Scheduling conflicts")
    for warning in conflicts:
        st.warning(warning)

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's plan from every pet's tasks, using Scheduler.")

if st.button("Generate schedule"):
    scheduler.generate_plan(owner)

    if scheduler.plan:
        st.success(f"Scheduled {len(scheduler.plan)} task(s) for today.")
        st.table(
            [
                {
                    "start_time": entry["start_time"],
                    "task": entry["task"].name,
                    "pet": pet_by_task_id.get(entry["task"].id, "Unknown pet"),
                    "duration_minutes": entry["task"].duration,
                    "priority": entry["task"].priority,
                }
                for entry in scheduler.plan
            ]
        )
    else:
        st.info("No tasks scheduled yet — add tasks above.")

    if scheduler.skipped:
        st.markdown("**Skipped:**")
        for entry in scheduler.skipped:
            pet_name = pet_by_task_id.get(entry["task"].id, "Unknown pet")
            st.warning(f"{entry['task'].name} ({pet_name}): {entry['reason']}")

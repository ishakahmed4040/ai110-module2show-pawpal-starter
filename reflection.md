# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Before drawing the UML, I started by identifying the three core actions a user needs to be able to perform in PawPal+:

1. **Add a pet** — the owner enters basic info about their pet (name, species/breed, etc.) so the app knows who the plan is for.
2. **Add/schedule a task** — the owner adds care tasks like walks, feeding, meds, or grooming, each with a duration and a priority, so the scheduler has something to work with.
3. **See today's plan** — the owner can view the generated daily schedule, in order, so they know what to do and when.

I used these three actions as the starting point for my UML design, since every class and method I sketched needed to support at least one of them.

From there, I landed on four classes:

- **Owner** — holds the pet owner's name, preferences, and the list of pets they own. Responsible for adding a pet and retrieving the list of pets.
- **Pet** — holds the pet's name, species, and its list of tasks. Responsible for adding, editing, removing, and retrieving that pet's tasks.
- **Task** — holds the details of a single care task: name, duration, priority, recurrence, and whether it's completed. Responsible for marking itself complete and checking whether it conflicts (time-wise) with another task.
- **Scheduler** — holds the available time for the day and is responsible for taking a pet's tasks and generating a feasible, prioritized daily plan, plus explaining why it chose that plan.

I kept `Owner` and `Pet` as simple data holders (using Python dataclasses) since their job is mostly to store information and manage their own lists. I split scheduling logic out into a separate `Scheduler` class rather than putting it on `Pet`, since scheduling felt like a distinct responsibility (it needs to reason about time/priority across tasks) rather than something a data class should own.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff: `Task.conflicts_with()` only flags a conflict when **both** tasks have an explicit `preferred_time` set. A task with no preferred time (a "flexible" task, like "Litter box cleaning") is never checked for conflicts against anything else, even though the scheduler still gives it a concrete start time when it packs it into the day.

I made this tradeoff because most pet care tasks (feeding, walks, meds) aren't tied to an exact minute in real life — treating every task as if it had a fixed time would force the owner to make up precise times for tasks they don't actually care about scheduling precisely, just so conflict detection would "see" them. In practice this is safe: flexible tasks are placed sequentially by the scheduler's cursor (right after whatever was scheduled before them), so they can never actually overlap another task's time window — they only ever fill gaps. The cost is that this reasoning lives implicitly in how `generate_plan` assigns start times; if that packing logic ever changed to place flexible tasks non-sequentially, `conflicts_with` would need to be revisited since it wouldn't catch overlaps between two flexible tasks or a flexible task placed inside a fixed task's window.

I also kept conflict detection as a simple O(n²) pairwise scan (`itertools.combinations` over all pending tasks) rather than a more efficient sweep-line/interval approach. For a single day's task list (realistically a handful to a few dozen items), the O(n²) scan is fast enough that the added complexity of an optimal algorithm wouldn't be worth it — simplicity and readability won out over asymptotic performance here.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used my AI coding assistant for essentially every phase: brainstorming the initial objects and their responsibilities, drafting the Mermaid UML, writing the class skeletons, implementing the scheduling/sorting/conflict/recurrence logic, writing tests, and wiring the Streamlit UI to the backend.

The feature that mattered most wasn't any single "smart suggestion" — it was that the assistant could directly read and edit my actual files (`pawpal_system.py`, `app.py`, `main.py`, tests) and then immediately *run* them (`pytest`, `python main.py`, even booting the Streamlit app) to prove a change worked, instead of me copy-pasting snippets and hoping. For example, after wiring the UI in Phase 6, it ran the app through Streamlit's `AppTest` harness to simulate clicking "Add pet" and "Generate schedule" and confirm no exceptions — that's a very different (and more trustworthy) kind of "help" than just generating plausible-looking code.

The most useful prompts were narrow and concrete, not open-ended — e.g., "how should the Scheduler retrieve tasks from the Owner's pets?" got a specific, actionable answer (`Owner.get_all_tasks()`), whereas vague prompts like "make it smarter" would have produced generic suggestions I'd have had to filter through anyway.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

During Phase 4's "Evaluate and Refine" step, I asked how `find_conflicts()` could be simplified. The AI offered two different directions: (1) replace the manual nested-loop pair-scan with `itertools.combinations(tasks, 2)`, and (2) replace the whole O(n²) approach with a sweep-line/interval algorithm for O(n log n) performance. I accepted the first (it's genuinely more readable, not just "clever") and rejected the second — a daily task list is realistically a handful to a few dozen items, so the sweep-line's better asymptotic performance wasn't worth the extra code complexity it would add. I verified both the accepted and rejected paths by actually re-running `main.py` and the test suite after the refactor to confirm identical output before keeping it, rather than trusting that the "more Pythonic" version was correct just because it looked cleaner.

I used separate chat sessions the way the project called for — one thread for algorithmic planning/brainstorming (Phase 4) and a fresh one for test planning (Phase 5) — and that mattered more than I expected. Keeping each session scoped to one concern meant the assistant's suggestions stayed relevant to that specific goal (e.g., the testing-focused session gave me edge cases like "same exact time" and "back-to-back tasks" instead of drifting back into implementation details), and it also gave me a clean, focused log to look back at later if I needed to remember *why* a particular test or algorithm decision was made.

The biggest thing I learned about being the "lead architect" is that the AI is excellent at execution once a decision is made — implementing a method, writing a test, catching an inconsistency (like a missing `task_id` on `Task`) — but it doesn't know my priorities unless I set them. Every actual tradeoff in this project (keeping `Owner`/`Pet` as simple dataclasses, treating tasks without a fixed time as "flexible," rejecting the sweep-line optimization) came from me deciding what mattered for *this* scenario's scale and goals, not from the AI volunteering the "right" answer unprompted. Using AI well here meant staying the one who owned the design decisions and used the assistant to move fast on everything downstream of them.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

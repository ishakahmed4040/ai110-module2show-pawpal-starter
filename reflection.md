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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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

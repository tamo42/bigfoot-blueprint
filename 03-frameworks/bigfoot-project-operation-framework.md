# Bigfoot Project Operation Framework

How one agent runs **one step** of an approved, scoped Bigfoot project, and then stops. Budget: 250 lines. Paired with the **Scoping Framework** (`bigfoot-project-scoping-framework.md`, which produces the PRD and phase docs this file operates on) and the **Orchestrator** (`bigfoot-project-orchestrator/`, which runs many steps in a row by starting a fresh agent for each). Adapted from Tax Sherpa OS `1073`. File naming (`<key>_prd.md`, `<key>_phase-<N>-<slug>.md`, `<key>_reference.md`, `<key>_evidence/`) is defined in the Scoping Framework.

## 1. The loop
An agent continuing a scoped project runs these seven moves, in order, and then stops. One session, one step.

1. **Load.** Read `GEMINI.md`, `.system-rules.md`, the project's `<key>_prd.md` phase index, the current phase doc by the read rule (§3), and the seed inputs its head names (always `<key>_reference.md`). The current phase is the first index row that is not Complete or Cancelled and whose `Depends on` phases are Complete. If its Approval cell is not `Approved <date> (Neal)`, or its status is Awaiting approval: there is no step, stop (§6). If its head carries an in-progress marker, take the next such row (§3). Read nothing else.
2. **Pick.** Take the Next-step block if it holds a step. If it holds none, or holds Blocked or Decision (§5), take the lowest-numbered step whose `Depends on` steps are done and in a phase with no marker. Within a phase the agent chooses; across phases it follows the PRD index. A step marked `Owner: <person>` or `(human)` is not startable by an agent: report it and stop.
3. **Mark.** Write the in-progress marker (§3) before touching anything else.
4. **Do.** Produce the step's one output from its stated Inputs, and only that.
5. **Verify.** Run the step's stated check against real output. A failed check means the step is not done.
6. **Write back.** Run the checklist (§4) and clear the marker.
7. **Stop.** End in exactly one outcome (§5). Do not start the next step; the next session does.

*Failure this prevents:* starting on an unclear step and proceeding anyway; a session that dies mid-step and leaves no trace; output built on an unchecked predecessor.

## 2. The step contract
A **step** is one verifiable output that one agent can produce in one session. It has four fields, written at the previous write-back (or at Mark, if picked from the Steps list):

| Field | Meaning |
| :-- | :-- |
| **Output** | The single artifact or state change that will exist when the step is done |
| **Inputs** | The files, decisions or earlier outputs it reads. Paths, not descriptions |
| **Done when** | The check that proves the output: an invariant if one exists, otherwise a real-data run, otherwise a named human look |
| **Depends on** | Step ids that must be done first |

Size rules:
- **One output.** Two independent outputs, or more than one session of work: split it.
- **No check, no step.** If "done when" cannot be stated, it is research (output: a written finding with sources) or a decision (§5), not a build step.
- **Human look is scheduled, not assumed.** A step whose only check is a human look ends as *decision needed*, naming the item. The agent never marks it done on its own judgment.
- **Small before scale (R-106).** A scrape, geocode or enrichment step runs on a small sample first and states the sample size; scaling up is a later, separate step.
- **Deploy steps are flagged.** A step whose output is a push to a site repo, a DNS change, or any other action that changes production is marked `Deploy` and `Owner: Neal`. Pushing a site repo deploys it (Railway), so an agent does not do it unless Neal's go is recorded in the step and the phase has an `Approved` stamp.

| Type | Output is | Done when (preferred order) |
| :-- | :-- | :-- |
| **Site code** (Astro, schema, templates) | A changed template or config that builds | `npm run build` passes and an invariant check or audit script passes on the built output, then a live sample after deploy |
| **Data** (scrape, geocode, merge) | A file or table of records in `/cache/` or the SQLite file | A small-sample run first (R-106), then counts, field-fill rates and a spot check against the public source (R-109) |
| **Enrichment** (LLM) | Enriched records | Strict JSON schema output (R-102), the Phase-1 7-question check before 20 (R-124), key names identical to the schema (R-125) |
| **Script / tool** | A script in `/scripts` or the workbench | Seeded bad-case test fails it, clean case passes it; documented in `scripts/README.md` (R-131) |
| **Research** | A written finding with sources | Each claim has a source; a named question is answered or marked unanswered |
| **External action** (GSC, DNS, GHL, Railway) | A configured setting | Observed end to end (a curl matrix, a test contact); usually `Owner: Neal` |

*Failure this prevents:* steps that look like phases, steps with no way to tell whether they worked, "done" resting on the agent's own say-so.

## 3. Phase-doc shape, read rule and ownership
A phase doc has five parts in fixed order. Everything above `## Log` is the **head**; the log is append-only, newest first.

```
# Phase <N>: <title> (Project: <key>)
**Status (<date>):** <status, §7> · <Approved <date> (Neal) | Approval: Pending>. Matches the PRD index.
**Writes:** <whole folders or repos this phase may create or edit>      **Seed inputs:** <reference, prior outputs>
## Why this phase exists        (≤ 5 lines)
## Steps                        (id, title, output, Depends on; Owner and Deploy flags)
## Acceptance criteria          (the checklist the readout reports on, §6)
## Next step
**In progress:** step <id> · <agent or tool> · started <date time> · touching: <paths>   (only while marked)
<the four step fields (§2) | Blocked: … | Decision: <id> | Scope changed: … | Awaiting approval: readout <path>>
## Log
### <date> · <step id> · <outcome>     (output path and evidence, decisions, notes; ≤ 12 lines)
```

**Budget and read rule.** The head is ≤ 60 lines. Read it whole, then only the three newest log entries; read further back only if the Next-step block names an entry. A head over 60 lines means the phase is too big: split it.

**The Next-step block** is rewritten at every write-back and holds exactly one form from §5.

**The in-progress marker** is the first line of the Next-step block, written at Mark and deleted last at write-back. It says who and which files, so a successor can read `git status` for exactly those paths.
- A phase with a marker is not taken. Pick another phase or end *blocked*: `Unblock by: Neal confirms the session is dead and clears the marker.`
- An agent never clears or overwrites another agent's marker, however old. Neal's chat answer that the session is dead lets the next step agent delete that one marker, quote the answer and date in its log, and re-run the step's check on the work under the marker's paths before trusting it.
- Work found under a dead marker's paths is untrusted until its step's check is re-run.
- A sister repo (a site under `bigfoot-sites/`) is outside this repo's `git status`: `touching:` names the repo, and a successor checks that repo's status too.

**Ownership.** The unit of ownership is the phase, held by whoever wrote its marker. Parallel agents work on different phases only, and their `Writes:` must not share a path.

| File | Who may write | How |
| :-- | :-- | :-- |
| Phase doc, its `Writes:` paths, `<key>_evidence/` files for that phase | The phase's marker holder | Anything inside the phase |
| `<key>_prd.md`, `01-context/project-index.md` | Any phase agent | Its own phase's index row or its own project's row only, by targeted edit; log entries append-only |
| Repo-root `.system-rules.md` | The agent, only when the step says to add a rule | Append a new `R-xxx`; never edit existing rules |
| Any other path | No one | A step needing it ends *scope changed* |

*Failure this prevents:* a phase doc too long to read; "what is next" found only by reading history; two agents editing one file.

## 4. Write-back checklist
Run at move 6, after Verify, in this order, so a session that dies partway leaves the marker standing.
1. **Phase log.** Add `### <date> · <step id> · <outcome>` at the top: output path, evidence (the number, the row count, the observed result). Item-level detail goes next to the item, not in a higher document.
2. **Decisions.** Gate each new decision by its dependents (§5). A cross-phase one adds its decision-phase row to the PRD index and edits the dependents' `Depends on` (a phase-index edit, so item 4 applies).
3. **Next-step block.** Write the proposed next step (four fields) or the `Blocked:` / `Decision:` / `Scope changed:` form under the marker line. Do not delete the marker yet.
4. **Status lines**, per the table below, each a targeted edit of one line: re-read the file just before editing, change only that line, never rewrite the file.
5. **Check.** Re-read the lines just written; the phase doc, PRD index row and any project-index row agree. A mismatch is fixed now, or the session ends *blocked* with the marker left.
6. **Clear the marker.** Delete it last. It states that every edit above landed.
7. **Commit** (only if the step says to, or the orchestrator does it): inside the one repo the step names. R-114: if the work would take more than 10-15 minutes to recreate, it is committed. Never `git push` a site repo (see §2, Deploy steps); never commit `.env` or credentials.

| Line | Updated by | When |
| :-- | :-- | :-- |
| Phase doc status line | Marker holder | Every write-back that changes the phase's status |
| PRD phase-index row | Marker holder | The same write-back as the phase doc line |
| `01-context/project-index.md` row | Marker holder | Only on a project-level change: phase 1 first starts, a phase completes with Neal's approval, project status changes |
| `Approved <date> (Neal)` stamp | The next session's agent, after Neal approves | At its first write-back, on the phase doc line and index row together |
Step-level progress lives only in the phase log and Next-step block. An agent never edits another phase's line.

**Drift rules.** (1) A phase-doc status change requires the same PRD index change in the same session. (2) The PRD keeps only the index line for a phase, never a copy of its detail. (3) A phase discovered mid-project gets its own doc and index row immediately, never scoped inline "for now". (4) A completed phase doc stands permanently; the PRD Decisions Log gets one completion entry.

## 5. Outcomes and stop conditions
A session ends in exactly one outcome. There is no "partly done": a step too big for one session was mis-sized, so stop as *scope changed* or split it.

| Outcome | Use when | Agent writes (log entry) | Next-step block becomes |
| :-- | :-- | :-- | :-- |
| **Done** | The "done when" check passed on real output | Output path and the check's evidence | The proposed following step (four fields) |
| **Blocked** | Work cannot proceed until a fact, access or event arrives from outside the documents, and no choice by Neal would change that | What is missing, who supplies it, the exact unblock action | `Blocked: <cause>. Unblock by: <action>.` |
| **Decision needed** | Work cannot proceed until Neal chooses between options, or the only check is a human look | The question, options, a recommendation, what the answer gates | `Decision: <id>` |
| **Scope changed** | The step cannot achieve its output as scoped, needs something out of scope, or shows the premise was wrong | What was found, why it breaks the scope, which phases it touches | `Scope changed: awaiting re-scope.` Do not improvise a new scope |

Rules:
- **Pick by the step, not the session.** If the output is done and verified but something else surfaced, the outcome is *done* and the finding is a logged decision. If two outcomes seem to apply, the more restrictive wins: scope changed, decision needed, blocked, done.
- **Blocked waits on a fact; decision needed waits on a choice.** Two options and a recommendation means a decision.
- **Never self-certify.** Marking a step done without a passing check, or resolving a decision that is Neal's, is a stop-condition failure.
- **Other steps stay pickable.** A blocked or decision-needed step does not stop the phase while another step has all its dependencies done.
- **Answers rewrite the block.** The agent that records Neal's answer logs it and rewrites the Next-step block in the same write-back.

**Gating a decision** by its dependents: none → logged in the phase with a recommendation, work continues; steps in the same phase → logged there, the dependent steps' `Depends on` names the decision id; another phase → its own **decision phase**: an index row whose output is the recorded decision, each dependent phase's `Depends on` edited to include it, status Blocked.

*Failure this prevents:* guessing past a choice that is Neal's; a decision buried in one log while another phase builds on it; "blocked" as a catch-all.

## 6. Phase-boundary readout
When the last step of a phase is done, the ending agent writes `<key>_evidence/<date>-phase-<N>-readout.md` (≤ 30 lines, no history) and stops:
1. **Acceptance criteria**, each met or not met with evidence (path, number, observed result). Not met is stated, not softened.
2. **Open decisions**, each *gated* (names the decision phase and what it blocks) or *not gated* (agent's recommendation).
3. **Scope changes**, or "none".
4. **Proposed next phase** and why now; anything Neal must settle first.
5. **Ask:** approve to close this phase and open the next, or name what to change. On a last phase add the three closure lines (§7).

The phase is not complete until Neal approves. Until then it stays *Awaiting approval*, the Next-step block reads `Awaiting approval: readout <path>`, and no later phase starts. On approval, the next session records the stamp.

## 7. Lifecycle and re-scope trigger
These are the only status values a status line may use.

| Term | Level | Means |
| :-- | :-- | :-- |
| Not started | phase | No step has started |
| In progress | phase | A step has started and another can be picked |
| Blocked | phase | No step can start (including *scope changed*) |
| Awaiting approval | phase | All steps done, readout written, Neal has not approved |
| Complete | phase | Neal approved the readout; stamp `Approved <date> (Neal)` |
| Cancelled | phase, project | Dropped by Neal; the doc stands |
| Draft | project | Scope not yet approved |
| Backlog | project | Scope approved, no phase started |
| Active | project | A phase has started |
| Parked | project | Neal stopped work for now; phase lines are not rewritten. Write `Resume when: <condition>` |
| Complete / Archived | project | Last phase Complete and closure written / closed and no longer loaded unless Neal names it |
Only Neal moves a project to Parked, Cancelled or Archived, or back from Parked. An agent never infers them.

**Closure.** On Complete or Cancelled, three lines go under `## Closure` in the PRD: **Delivered** (what "done looks like" asked for against what exists, unmet items named); **Cost** (the one thing that took longest or surprised us); **Carry forward** (one change for the next project, or a rule for `.system-rules.md` if it has repeated 3-5 times).

**Re-scope trigger.** A change is **material** when a statement Neal already approved would become false. The agent proposes the tier (the larger if unsure); Neal confirms.

| Change | Tier | Goes next |
| :-- | :-- | :-- |
| The objective, or an item added to or removed from the out-of-scope list | Whole PRD | Every open phase Blocked; PRD back to Draft; Neal re-approves through the Scoping Framework |
| An approved phase's output, acceptance criteria, `Writes:` or `Depends on`; a phase removed or split; a phase's premise found false | Affected phases | Those and downstream phases go back through scoping; the rest continue |
| Steps added, split, reordered or reworded inside a phase; a decision settled within its options; a newly found phase or decision phase | Not material | Log it and carry on |

The agent never re-scopes. It ends *scope changed* with a re-scope request: proposed tier, the change, the approved statement it falsifies, the phases affected. The procedure is in the Scoping Framework.

## 8. Kickoff prompt and cold-start test
**Kickoff prompt** (paste into any agent; fill in the PRD path):
```
Continue the project whose PRD is <path to <key>_prd.md> under 03-frameworks/bigfoot-project-operation-framework.md. Run its §1 loop for one step, then stop.
1. Load as §1 says, reading the phase doc by the §3 read rule.
2. Before any edit, state the phase's status and whether its Next-step block carries an in-progress marker.
3. Awaiting approval, or Approval Pending: there is no step to pick. Report what Neal must approve and stop.
4. Marker present: the phase is another agent's. Never clear it. Pick another phase, or end blocked (§3).
5. Block reads Scope changed: report it and stop. Blocked or Decision: read the block and the log entry it names; do not guess past it. Take another startable step or stop and report.
6. A step marked Owner: <person>, (human) or Deploy is not yours: report it and stop.
7. Write the marker before any other edit. Write back in the §4 order, clearing the marker last. End in one §5 outcome.
```
**Cold-start test.** Checks that the documents alone carry the handoff. Neal picks a project just after a write-back and states the step he expects next. A new session, not the one that wrote the last write-back, gets the kickoff prompt plus `Cold-start test: stop after Pick. Change no file and ask no questions.` It may read only what §1 Load names. It must state (a) the phase status and marker state, (b) the next step as four fields, or the §5 form, or "none: Awaiting approval", (c) the files it read. Record in `<key>_evidence/<date>-phase-<N>-cold-start.md` (≤ 10 lines). **Pass:** all stated correctly, matches Neal's step, a stop case is reported as a stop, no file read outside §1. **Fail:** anything else, including a question the documents should have answered; fix the line that misled it and rerun with another new session.

*Failure this prevents:* a handoff that works only because the successor shares the predecessor's memory; improvising past a stop.

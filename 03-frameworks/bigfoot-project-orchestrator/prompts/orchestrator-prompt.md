# Orchestrator prompt

Neal pastes the block under "Paste text" into a fresh VS Code Claude chat, with the project's PRD path filled in. The main chat is the loop (subagents cannot spawn subagents, so the loop cannot itself be a subagent); it spawns the step agent and the verifier as fresh background agents. Loop logic: `03-frameworks/bigfoot-project-operation-framework.md` (the **Operation Framework**, §-numbers below). Adapted from the Tax Sherpa OS `1074` orchestrator.

## Paste text
```
You are the orchestrator for the Bigfoot project whose PRD is <path to <key>_prd.md> (optional: max steps <n>, default 5). You run the loop in 03-frameworks/bigfoot-project-operation-framework.md step by step with fresh agents, and stop only at the stop states below. Read 03-frameworks/bigfoot-project-orchestrator/prompts/orchestrator-prompt.md now and follow it exactly. You never edit a project file yourself, never record an approval, never clear a marker, never push a site repo and never run a Deploy step. You push the control-plane repo (nhq-bigfoot-blueprint) once, at a stop.
Neal's answer to the last stop, if any: "<quoted answer>" (<date>)   [leave this line out on a first run]
```

## What you do
You never read a step agent's reply as the outcome, and you never decide anything that is Neal's (Operation Framework §3, §5, §6, §7). All state lives in the documents, so a new chat with the same paste text resumes from the Next-step block. Paths below are relative to `C:\Users\tamo4\git\nhq-bigfoot-blueprint` unless a site repo is named; `<proj>` is the folder holding the PRD; `<key>` is the PRD's file prefix.

### 0. Run start (once)
1. Open the run log `<proj>/<key>_runs/<date>/<time>-run.log` (create the folders). Append every line as the action happens, never at the end. Line format: `<ISO time> | <type> | <key>.<phase>.<step> | <detail>`. Types: READ, SPAWN, CHECK, OUTCOME, VERIFY, COMMIT, PUSH, STOP. If the newest earlier log does not end in STOP, write a READ line saying the last run ended mid-run.
2. Run `git status` for the control-plane repo and for every site repo that a marker or a `Writes:` line names. Not clean: STOP S12 before spawning anything.
3. Count steps as you go. At the step cap: STOP S14.

### 1. Read state (each iteration; the first row that matches ends the read)
Read only what Operation Framework §1 names: `02_context_boundary.bleep.md`, `.system-rules.md`, the PRD, the project's row in `01-context/project-index.md`, the current phase doc by the §3 read rule (head, then newest three log entries), and the `<key>_reference.md` it names. Log a READ line naming the row.

| Row | Check | If true |
| :-- | :-- | :-- |
| R1 | PRD or `project-index.md` status is Parked, Cancelled, Archived or Complete | STOP S1 |
| R2 | Run start only: tree not clean | STOP S12 |
| R3 | Run start only: a phase's `Writes:` enter a protected path (a `.env` or credentials file, or any repo other than the control plane and the project's named site repos, such as `neal-os`, `tax-sherpa`, `resilient-roots`) | STOP S13 |
| R4 | Current phase = first PRD index row not Complete or Cancelled whose `Depends on` phases are all Complete. When the PRD allows either order, index order decides. No such row | STOP S2 |
| R5 | That phase's head carries an in-progress marker | Take the next qualifying row; none left: STOP S3 |
| R6 | Status Awaiting approval (block reads `Awaiting approval: readout <path>`) | STOP S4 |
| R7 | Index Approval cell is not `Approved <date> (Neal)` and status is not Awaiting approval | STOP S5 |
| R8 | Next-step block is `Scope changed: ...` | STOP S6 |
| R9 | Block is a four-field step, `Blocked:` or `Decision: <id>` | Go to R10 |
| R10 | Pick a startable step: the block's step, or with Blocked or Decision the lowest-numbered step whose `Depends on` steps are done and which no Decision id gates. A step marked `Owner: <person>`, `(human)` or `Deploy` is not startable by an agent. None startable here: if another qualifying phase has a `Writes:` set that does not overlap, go to R5 for it; else STOP S15 when a step is startable but for its owner or Deploy flag, else STOP S7. Otherwise CONTINUE |

### 2. Spawn the step agent
Spawn one fresh background agent. Its prompt is `prompts/step-agent-prompt.md` with the PRD path, the step id when two phases are startable, and Neal's quoted answer with its date when this iteration follows a stop. Never hand it an answer to record from your own judgment.
- Set the ETC: the median SPAWN-to-OUTCOME of the same role on this run, else 15 min for a step agent and 5 min for a verifier; a step with its own estimate in the phase doc uses that. Log SPAWN with agent id and ETC.
- Arm a Monitor for 50% and 125% of the ETC (one Monitor waits at most 30 min; chain them for longer). Cancel it on the agent's notification.
- At 50% and 100%: check progress (a file under the marker's `touching:` paths changed, or the agent's progress file grew); log CHECK. At 125%: progress in the last 25%: recalculate and keep waiting. None: stop the agent with TaskStop, leave its marker, STOP S11.
- Foreground `sleep` is blocked; wait on the Monitor or the task notification.

### 3. Read the outcome
When the agent returns, re-run R5 to R8 on the phase doc and read the newest log header `### <date> · <step> · <outcome>` as the outcome. Log OUTCOME. Unreadable (no new log line, the marker still present, an outcome outside Done, Blocked, Decision needed, Scope changed, or the log line and Next-step block disagree): STOP S11. Never clear the marker; the step is not done.

### 4. Verify
Spawn a fresh verifier (`prompts/verifier-prompt.md`) with the project dir, phase number, the marker's `touching:` paths read before the step, the repos in play, and base ref `HEAD`. It checks V1 marker cleared, V2 status lines agree, V3 no credentials in added lines, V4 no unexpected binaries, V5 the diff inside the phase's `Writes:` plus the shared status files, V6 protected paths untouched. Log VERIFY.
- V3 is `python -I scripts/secret_scan.py <repo> ...` and has no allowance beyond its placeholder rules. A V3 HIT does not stop the run the first time: spawn one scrub agent (the step agent's spawn text plus "Scrub only: remove these HIT lines, shown here as file:line, by replacing each secret with a placeholder like `YOUR_API_KEY` and reading the value from the environment; change no other behavior; record nothing else; do not touch the Next-step block or the log outcome"), log SPAWN as `scrub`, then re-verify. A secret that was real must also be rotated: that is Neal's, so the digest says so.
- Any other FAIL, the same failure twice, a V3 HIT that remains after the scrub, or a commit failure: STOP S14, commit nothing. Waiving a hit is Neal's only.

### 5. Commit
After a pass, commit the step: `<key>: <step id> <one-line result>`, inside the one repo the step names (the control-plane repo for documents and scripts; a site repo only if the step edited it). Do not push per step. A commit failure is S14. Log COMMIT with the hash and `no push yet`. R-114 applies: work that would take more than 10-15 minutes to recreate is committed, which every verified step is.

### 6. Decide
| Outcome | Next |
| :-- | :-- |
| Done, block is a four-field step | Back to step 1 |
| Done, block is Blocked, Decision or Scope changed | Back to step 1: R8 stops on Scope changed (S6); R10 takes another startable step, else S7 or S15 |
| Done, readout written, phase Awaiting approval | The verifier also confirms the readout exists and is at most 30 lines; commit; STOP S4 |
| Blocked | Back to step 1; no other startable step: STOP S8 |
| Decision needed | Back to step 1; no other startable step not gated by the decision: STOP S9 |
| Scope changed | STOP S10 |

## Stop states and digests
**Push, once per run.** At a stop other than S12, S13 and S14, if the control-plane repo holds commits this run made that are not on the remote, run `git push` for that repo once, after the last commit and before the digest. Log PUSH with the commit range. A denied or failed push is not retried or worked around: show it in the digest as an item for Neal. **Never push a site repo** under `C:\Users\tamo4\git\bigfoot-sites\`: a push there deploys production (Railway) and is Neal's. If a site repo holds unpushed commits from this run, the digest lists them and the exact repo for Neal.

Every stop writes `<proj>/<key>_runs/<date>/<time>-digest.md` (one screen) and a last STOP log line, shows the digest in chat, and ends the run. The digest has: **Look at**, **Options**, **Recommend**, **Your answer does**. Neal answers in chat; you never write the answer into the documents. On resume the next paste carries the quoted answer to the step agent.

| Id | State | Action and digest |
| :-- | :-- | :-- |
| S1 | Project Parked, Cancelled, Archived or Complete | Run nothing. Look at the PRD status and its `Resume when` or `Closure` line. Recommend leave. Only Neal changes it |
| S2 | No phase qualifies (all Complete or Cancelled, or open phases wait on a phase not Complete) | Look at the PRD index; say "all Complete" or "open phases wait on <phase>" with its status; name the phase that needs Neal |
| S3 | In-progress marker on every qualifying phase | Never clear it, never edit under its `touching:` paths. Show the marker (agent, start, paths), `git status` for those paths and its age as information only. Options: wait, or Neal answers the session is dead. A dead-session answer authorizes the next step agent to delete the marker, quote the answer and date in its log, and re-run the step's check on the work under those paths |
| S4 | Phase Awaiting approval | No step exists. Look at the readout path. Options: approve, or name what to change. Recommend approve if every criterion reads met. The next step agent stamps `Approved <date> (Neal)` |
| S5 | Approval cell not `Approved` | Look at the phase head and index row. Options: approve, change scope, leave. Stamped as S4 |
| S6 | `Scope changed: awaiting re-scope` | Pick no other step. Look at the log entry's re-scope request (tier, change, falsified statement, phases). Recommend the tier proposed, the larger if unsure. Neal runs the re-scope by hand |
| S7 | No startable step anywhere | Look at each blocked step's `Unblock by:` or `Decision: <id>` entry. Recommend the entry's recommendation |
| S8 | Last outcome Blocked, no other startable step | Look at the log entry: what is missing, who supplies it, the unblock action |
| S9 | Last outcome Decision needed, no other startable step | Look at the entry's question, options, recommendation and what the answer gates |
| S10 | Last outcome Scope changed | As S6 |
| S11 | Outcome unreadable or agent stopped for no progress | Never clear the marker; the step is not done. Look at the phase head and `git status` for the `touching:` paths. Options: Neal answers the session is dead and the step reruns (recommended), or Neal reads the partial work |
| S12 | Dirty tree at run start | Spawn nothing. Look at `git status`. Options: Neal commits or discards by hand, or confirms the changes are another session's. Recommend Neal looks first |
| S13 | A phase's `Writes:` enter a protected path | Refuse. Look at the `Writes:` line. Recommend running that step by hand outside this orchestrator. Not resumable here |
| S14 | Verifier failure, the same failure twice, a credential hit that survived the one scrub, a commit failure, or the step cap | Look at the failing check and evidence, or the step count. Options: fix and rerun once (recommended), or raise the cap. A real credential hit needs Neal to look and rotate the key before anything is committed |
| S15 | Every startable step is owned by a person or flagged Deploy | Spawn nothing. Name the owner, the step's output and, for a Deploy step, the commits to push and the repo. Options: Neal does it and says so in chat, or Neal reassigns it to an agent. Recommend Neal does it |

## Rails (all runs)
- One commit per step, after the verifier passes. One push of the control-plane repo per run, at the stop (not at S12, S13, S14). Never a site repo.
- Never mark a step done without its own check; never record an approval or resolve a decision without Neal's chat answer.
- Never clear or edit another agent's marker; you never clear one yourself.
- Never run a step that scrapes or enriches at scale unless the step itself states a small sample size (R-106); a step that would spend paid API credits beyond what the step names ends *blocked*.
- Parallelism only across phases whose `Writes:` do not overlap (Operation Framework §3).
- Run detail belongs in `<proj>/<key>_runs/<date>/` only; the PRD and phase docs hold no run history.
- Not known until the pilot: whether step agents inherit this chat's permissions (a denied action may end a step Blocked); whether the Monitor timers survive a closed chat.

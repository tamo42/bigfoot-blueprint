# Bigfoot Project Orchestrator: Operator SOP

Written for a reader with no memory of this project. You need the VS Code Claude chat and this page. You never run a terminal command.

Part of the paired set in `03-frameworks/`: the **Scoping Framework** (`../bigfoot-project-scoping-framework.md`) writes a scope; the **Operation Framework** (`../bigfoot-project-operation-framework.md`) says how one agent does one step; this **Orchestrator** does many steps in a row. Adapted from the Tax Sherpa OS `1074` orchestrator.

## 1. Operational Purpose (The Why)
Running a scoped project by hand means pasting a kickoff for every step, then asking for a commit. The orchestrator does that loop for you. From one pasted prompt, the chat reads the project's state, starts a fresh agent for one step, reads the outcome from the phase log, starts a second agent to verify the work, commits the step, and continues. It stops only when a framework stop state needs you, shows a one-screen digest, and resumes when you answer in chat.

It never approves anything, resolves a decision, clears another agent's marker, runs a Deploy step, or pushes a site repo. Those stay yours. A push to a site repo under `bigfoot-sites/` deploys that website.

## 2. Execution Cadence (The When)
- Run it when a scoped project has steps waiting and you want several done without pasting a kickoff each time.
- Run it again after every stop, once you have answered the digest.
- Do not run it on a Parked, Cancelled, Archived or Complete project, on a project whose phases write to credentials or to another repo (`neal-os`, `tax-sherpa`, `resilient-roots`), or while another session is working in the same repo.
- One run is capped at 5 steps unless the paste text says otherwise. Start a new chat with the same paste to continue.
- Steps that scrape, geocode or enrich run on the small sample their step states (R-106); scaling up is a separate step you will see as its own item.

## 3. Prerequisites & Environment
- The VS Code Claude chat, a fresh conversation.
- The project is scoped under the Scoping Framework: a `<key>_prd.md`, phase docs `<key>_phase-<N>-<slug>.md` and a `<key>_reference.md` in its `02-workbench/` folder, and a row in `01-context/project-index.md`. You know the PRD path.
- The `nhq-bigfoot-blueprint` working tree is clean (every earlier change committed). So is any site repo the project writes to. If not, the run stops at once (S12).
- Each run writes a log and any digest to `<project folder>/<key>_runs/<date>/`.

## 4. Step-by-Step Execution (The How)
1. Open a fresh VS Code Claude chat.
2. Copy the text between the lines below and fill in the PRD path. Keep the text word for word otherwise.

```
You are the orchestrator for the Bigfoot project whose PRD is <path to <key>_prd.md> (optional: max steps <n>, default 5). You run the loop in 03-frameworks/bigfoot-project-operation-framework.md step by step with fresh agents, and stop only at the stop states below. Read 03-frameworks/bigfoot-project-orchestrator/prompts/orchestrator-prompt.md now and follow it exactly. You never edit a project file yourself, never record an approval, never clear a marker, never push a site repo and never run a Deploy step. You push the control-plane repo (nhq-bigfoot-blueprint) once, at a stop.
Neal's answer to the last stop, if any: "<quoted answer>" (<date>)   [leave this line out on a first run]
```

3. Send it. The chat works through the loop and logs each action. You can watch the log file grow in `<key>_runs/<date>/`.
4. When it stops, it shows a digest with four parts: **Look at**, **Options**, **Recommend**, **Your answer does**. Look at the item named, then answer in chat in plain words.
5. To continue, open a fresh chat, paste the same text, and fill the last line with your answer in quotes and today's date. The next step agent records your answer in the project documents, then does its step. Never edit the project documents by hand to record an answer.
6. A run ends in a stop. Nothing is lost between runs: all state lives in the documents.

### How to answer each stop
| Id | When it appears | How to answer |
| :-- | :-- | :-- |
| S1 | The project is Parked, Cancelled, Archived or Complete | Nothing to answer. Only you change that status, by hand, if you want it running again |
| S2 | No phase qualifies (all done, or open phases wait on another) | Read which case the digest names. If a waiting phase needs your approval or decision, do that and rerun. Otherwise the project is finished |
| S3 | Every qualifying phase has another session's in-progress marker | Wait and rerun later, or answer in chat that the session is dead (for example: "The session on phase 2 is dead, clear its marker"). The next step agent then deletes the marker and re-checks the work under it |
| S4 | A phase is Awaiting approval | Read the readout the digest names. Answer "approve phase N" or say what to change. The next step agent stamps your approval |
| S5 | A phase has not been approved | Look at the phase head. Answer "approve phase N", "change <what>", or "leave it" |
| S6 | Scope changed, awaiting re-scope | Read the log entry's re-scope request. You run the re-scope under the Scoping Framework. Nothing is rerun until the block is cleared |
| S7 | No step can start anywhere | Read each blocked step's `Unblock by:` or `Decision:` entry. Do what it names or answer the decision, then rerun |
| S8 | A step is Blocked and nothing else can start | Supply what is missing (a fact, access or event), say so in chat, and rerun |
| S9 | A step needs your decision | Read the question and options. Answer with one option. The next step agent records it and rewrites the Next-step block |
| S10 | A step ended Scope changed | Same as S6 |
| S11 | The outcome was unreadable, or an agent made no progress and was stopped | Read the digest's `git status` lines. Recommended answer: "the session is dead, rerun the step". Or read the partial work first. The marker stays until you answer |
| S12 | The working tree is not clean at the start | Look at the changed files. Commit or discard them yourself, or say they belong to another session and wait. Rerun when clean |
| S13 | A phase writes to credentials or another repo | The project cannot run here. Run its steps by hand. Not resumable |
| S14 | The verifier failed, failed twice, found a credential it could not scrub, a commit failed, or the step cap was reached | Read the failing check. Recommended answer: "fix and rerun once". To continue past a cap, rerun with a higher max steps. A real credential hit needs your look, and the key must be rotated, before anything is committed |
| S15 | Every startable step belongs to a person, or is a Deploy step | The digest names the owner, the output and, for a Deploy step, the commits and repo to push. Do it (for example push the site repo, change a DNS record, click in Search Console) and tell the chat, or answer "reassign it to an agent". Recommended: you do it |

## 5. Troubleshooting & Known Limitations
- **The run stops at once with S12.** The tree has uncommitted changes. This protects you from mixing runs; clear it and rerun.
- **A marker stays after a stop.** That is on purpose: it tells the next session where the last one stopped. Only your chat answer that the session is dead lets an agent delete it.
- **The chat ran out of room or you closed it.** Open a fresh chat and paste the same text. The documents hold the state; the run resumes from the Next-step block. A step in flight when the chat closed may have left a marker (S3 and S11).
- **A step ended Blocked on a denied action.** Step agents may not inherit the chat's permissions. Allow the action or do it by hand, then rerun. Not yet confirmed for every case (see Pilot).
- **Timers.** The chat checks each agent at 50%, 100% and 125% of an estimated time and stops one that shows no progress. Whether the timers survive a closed chat is not yet known.
- **Rollback.** Each step is one commit, so a bad step is undone by reverting that commit. Ask the chat to do it; do not run commands yourself. A site that has already been deployed is rolled back by reverting and pushing the site repo, which is yours to do.
- **One push per run.** The orchestrator commits each step and pushes `nhq-bigfoot-blueprint` once, when the run stops (not after a verifier failure, a credential hit or a dirty-tree stop). It never pushes a site repo. If Claude Code denies the push, the digest says so; allow it with a Bash permission rule for `git push` or push by hand.
- **Credentials.** Step agents read keys from the environment and write placeholders; the verifier runs `scripts/secret_scan.py` on every step. If a real key was ever committed, treat it as leaked and rotate it.
- **Where to look.** Run logs and digests: `<key>_runs/<date>/`. The agent prompts: `prompts/`. You do not need to read them to run this.

## Pilot (not yet run)
This orchestrator has been adapted but never run on a Bigfoot project. Pilot it on `p4_canonical` (`02-workbench/03-wells-water-well-drillers/p4_canonical_trailing_slash_plan.md`) once Neal has approved Phase 1. Success: it runs 3 consecutive startable steps with no human input outside a stop state, and the pilot reports what stopped the run. Note: that project's steps `2.5` and `3.6` (commit and deploy) are Deploy steps and will stop the run at S15, which is the designed behavior. If the pilot fails that test, drop or redesign this orchestrator rather than patching it.

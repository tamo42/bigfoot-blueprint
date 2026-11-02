# Step-agent prompt

The orchestrator spawns one fresh background agent per step with the block under "Spawn text", filling the `<...>` slots and dropping the optional lines that do not apply. The agent is a new session: it has the documents, not the orchestrator's memory. The kickoff is the Operation Framework §8 kickoff, copied; if that kickoff changes, change this prompt to match.

## Spawn text
```
Continue the project whose PRD is <path to <key>_prd.md> under 03-frameworks/bigfoot-project-operation-framework.md. Run its §1 loop for one step, then stop.
1. Load as §1 says, reading the phase doc by the §3 read rule.
2. Before any edit, state the phase's status and whether its Next-step block carries an in-progress marker.
3. Awaiting approval, or Approval Pending: there is no step to pick. Report what Neal must approve and stop.
4. Marker present: the phase is another agent's. Never clear it. Pick another phase, or end blocked (§3).
5. Block reads Scope changed: report it and stop. Blocked or Decision: read the block and the log entry it names; do not guess past it. Take another startable step or stop and report.
6. A step marked Owner: <person>, (human) or Deploy is not yours: report it and stop.
7. Write the marker before any other edit. Write back in the §4 order, clearing the marker last. End in one §5 outcome.

Run rules from the orchestrator:
- Step: <id>   [only when two phases are startable; take this step and no other]
- Neal's answer to the last stop: "<quoted answer>" (<date>)   [leave out on a first run]
  Record it before your step, in the §4 order, and only as the framework allows: a decision answer is logged and the Next-step block rewritten (§5 "Answers rewrite the block"); an approval is stamped as `Approved <date> (Neal)` on the phase status line and the PRD index row together (§4, §6); an answer that the session holding a marker is dead lets you delete that one marker, quote the answer and its date in your log entry, and re-run the step's check on the work under the marker's `touching:` paths before you trust it. Record nothing the answer does not say. If it does not match what the documents are waiting on, do nothing with it and end Blocked, naming the mismatch.
- Progress file: write `<project folder>/<key>_runs/<date>/<time>-step-<id>-progress.md` and append one line at Mark, at each sub-result and at Verify. The orchestrator reads it, and the files under the marker's `touching:` paths, to tell you are working.
- Do not commit and do not push. The orchestrator commits after an independent check and pushes the control-plane repo at the end of the run. You never push anything, and you never run a Deploy step.
- Never decide what is Neal's: approve a phase, settle a decision, clear a marker without his quoted answer, or re-scope. Those end the step as Decision needed, Blocked or Scope changed.
- Leave the tree with only your step's edits: the phase's `Writes:` paths and the shared status lines §3 allows. Add no binaries unless the phase's `Writes:` names them (for example a site's `*.sqlite`). Put no API key, token, password, connection string or `.env` content in any file; read credentials from the environment and use placeholders like `YOUR_API_KEY` in examples. Raw scraped data stays in `/cache/` or the places the step names.
- Small before scale (R-106): a scrape, geocode or enrichment step runs on the sample size the step states. Do not run a larger pull, and do not spend paid API credits beyond what the step names; if the step needs more, end Blocked or Decision needed.
- Self-scan before Verify and again before write-back: run `python -I scripts/secret_scan.py .` from the control-plane repo root (add each site repo you touched). Any HIT line is yours to fix now; the step is not done while one remains. The verifier runs the same script, so a clean self-scan means V3 passes.
- Your last act is the §4 write-back with the marker cleared; the newest `### <date> · <step> · <outcome>` log header is your result. The orchestrator reads that header, not your reply, so end with one line: the outcome word and the log header.
```

## Notes for the operator of this prompt
- The progress file must sit inside the phase's `Writes:` paths so the verifier's V5 passes; if the phase's `Writes:` do not cover `<key>_runs/`, the orchestrator names another folder in the spawn that they do cover.
- Not known until the pilot: whether the agent inherits the chat's permissions; a denied action ends the step Blocked with the denial named.

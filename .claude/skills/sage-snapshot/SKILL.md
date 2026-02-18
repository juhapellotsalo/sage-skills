---
name: sage-snapshot
description: "Persist current development state to SAGE-STATE.md for session handoff"
disable-model-invocation: true
---

# Sage Snapshot

Persist the current development state for session continuity.

## Core Principle

Write **just enough for an agent to resume** — not documentation, not history. If someone needs details, they read the code or git log.

## Instructions

1. Analyze the current conversation

2. Check for uncommitted changes (`git status`). If there are any, ask the user whether to commit them before snapshotting.

3. Extract and update each section of `SAGE-STATE.md` (project root) with **minimal viable context**:

   - **Now** — What we're working on (1 sentence)
   - **Recent** — Last few things done, newest first (5 bullets max)
   - **Decisions** — Only active architectural choices that affect ongoing work
   - **Open** — Unresolved questions blocking or guiding next steps
   - **Next** — 2-3 immediate priorities

4. If `SAGE-STATE.md` doesn't exist, create it using this template:

   ```markdown
   # SAGE State

   ## Now
   *What we're actively working on*

   ## Recent
   *Last few things done (newest first)*
   -

   ## Decisions
   *Key technical choices and why*
   -

   ## Open
   *Unresolved questions, things to figure out*
   -

   ## Next
   *Immediate priorities when resuming*
   -
   ```

5. Confirm what was captured (one sentence)

## Pruning Rules

- **Recent**: Drop items beyond 5 — if work is significant, it's in git history
- **Decisions**: Remove tactical decisions that are now obvious or baked into code
- **Open**: Delete resolved questions entirely, don't mark them done
- If state file feels bloated, tell the user and prune aggressively

## Anti-patterns

- Don't write paragraphs — bullets only
- Don't explain why decisions were made in detail — just the decision
- Don't keep history — that's what git is for
- Don't document code — that's what code comments are for

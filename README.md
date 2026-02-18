# sage-skills

A collection of Claude Code skills, subagents, and hooks that I use daily. Everything is prefixed with `sage-` so skills are easy to find in the slash command menu and subagents are immediately identifiable in execution logs.

## The two-pass workflow

The core idea: a single-pass build always has omissions and bugs. A two-pass approach — build, then review with a different persona — catches things the dev persona never would, because it's operating with different instructions.

1. Run `/sage-dev`, prompt the task. This persona has instructions on how to write code, what patterns to follow, what to pay attention to.
2. Commit the work. Run `/sage-review` to switch to the reviewer persona. This runs an adversarial code review and surfaces a prioritized list of issues — then fixes them.
3. Run `/sage-snapshot` before ending the session to persist state for next time.

Quick, repeatable, and the quality difference between one-pass and two-pass is clear.

## Installation

Copy into any project's `.claude/` directory:

```
.claude/skills/sage-dev/SKILL.md
.claude/skills/sage-review/SKILL.md
.claude/skills/sage-snapshot/SKILL.md
.claude/agents/sage-scout.md
.claude/agents/sage-search.md
.claude/hooks/sage-check-deps.py
```

---

## Skills

### `/sage-dev` — Build mode

Pragmatic senior developer persona. Understands the problem before coding, writes clean code on the first pass, avoids over-engineering. Makes conscious trade-offs and iterates in small, working increments.

### `/sage-review` — Review mode

Critical senior engineer persona. Adversarial code review focused on clarity, simplicity, and real-world failure modes. Points to specific lines, assigns severity, recommends deletion when warranted. Finds issues and fixes them.

### `/sage-snapshot` — Persist state

Captures minimal session state to `SAGE-STATE.md` in the project root. Designed for session handoff — just enough context for an agent (or you) to resume later. The dev and review skills read this file automatically on activation.

---

## Subagents

The primary purpose of these is to offload token-heavy operations to a subagent, preserving the main agent's context window for the actual work.

### sage-scout

Explores the current project's structure, tech stack, dependencies, configuration, code patterns, and git state. Returns a structured report so the main agent doesn't need to scan the codebase itself. Use at the start of a session or when switching to an unfamiliar project.

### sage-search

Searches external sources — GitHub repos, web documentation, package registries. Uses `gh` CLI, WebSearch, and WebFetch. Returns a concise summary with findings and sources. Used by the dependency hook automatically, or on demand for any research task.

---

## Hooks

LLM training data is always behind, so the agent defaults to library versions that are often outdated. The hook forces it to run a sage-search to look up the latest versions.

### sage-check-deps

Fires on `PostToolUse` whenever a dependency file (`package.json`, `pyproject.toml`, `requirements.txt`) is written or edited. Detects newly added packages and instructs the agent to use the sage-search subagent to verify latest stable versions and known vulnerabilities.

Projects can opt out by placing a `.skip-dep-check` file anywhere in the directory hierarchy.

Register it in your `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/sage-check-deps.py"
          }
        ]
      }
    ]
  }
}
```

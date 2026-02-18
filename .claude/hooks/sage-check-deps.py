#!/usr/bin/env python3
"""
Hook that triggers when dependency files are modified.
Only reminds Claude to verify versions when NEW dependencies are added.
"""
import json
import os
import re
import sys

SKIP_MARKER = ".skip-dep-check"


def is_skipped(file_path: str) -> bool:
    """Walk up from the dependency file's directory looking for a skip marker."""
    directory = os.path.dirname(file_path)
    home = os.path.expanduser("~")
    while True:
        if os.path.isfile(os.path.join(directory, SKIP_MARKER)):
            return True
        parent = os.path.dirname(directory)
        if parent == directory or directory == home:
            return False
        directory = parent


# Dependency file patterns and their package managers
DEPENDENCY_FILES = {
    "pyproject.toml": "PyPI",
    "requirements.txt": "PyPI",
    "package.json": "npm",
}


def extract_dependencies(content: str, filename: str) -> set[str]:
    """Extract dependency names from file content based on file type."""
    deps = set()

    if filename == "pyproject.toml":
        matches = re.findall(r'["\']([a-zA-Z0-9_-]+)(?:\[.*?\])?(?:[><=!~]|$)', content)
        deps.update(match.lower() for match in matches)

    elif filename == "requirements.txt":
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith(("#", "-")):
                match = re.match(r"([a-zA-Z0-9_-]+)", line)
                if match:
                    deps.add(match.group(1).lower())

    elif filename == "package.json":
        try:
            data = json.loads(content)
            for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
                if key in data and isinstance(data[key], dict):
                    deps.update(data[key].keys())
        except json.JSONDecodeError:
            matches = re.findall(r'"(@?[a-zA-Z0-9_/-]+)"\s*:\s*"[^"]*"', content)
            deps.update(matches)

    return deps


def main():
    data = json.load(sys.stdin)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Check if this is a dependency file
    filename = file_path.split("/")[-1]

    if filename not in DEPENDENCY_FILES:
        sys.exit(0)  # Not a dependency file, nothing to do

    if is_skipped(file_path):
        sys.exit(0)  # Project opted out via .skip-dep-check marker

    package_manager = DEPENDENCY_FILES[filename]
    new_deps = set()

    if tool_name == "Edit":
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")

        old_deps = extract_dependencies(old_string, filename)
        new_deps_in_new = extract_dependencies(new_string, filename)

        new_deps = new_deps_in_new - old_deps

    elif tool_name == "Write":
        content = tool_input.get("content", "")
        new_deps = extract_dependencies(content, filename)
        if new_deps:
            deps_list = ', '.join(sorted(new_deps)[:10])
            more = '...' if len(new_deps) > 10 else ''
            feedback = f"""DEPENDENCY FILE WRITTEN: `{filename}`

Use the sage-search subagent to verify that these packages use current stable versions from {package_manager}: {deps_list}{more}

The subagent should check the latest stable version for each package and flag any that are outdated or have known security issues.
"""
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": feedback,
                }
            }
            print(json.dumps(result))
        sys.exit(0)

    if not new_deps:
        sys.exit(0)

    deps_list = ', '.join(sorted(new_deps))
    feedback = f"""NEW DEPENDENCY DETECTED in `{filename}`:

Added: {deps_list}

Use the sage-search subagent to verify these new packages on {package_manager}. The subagent should check:
1. Latest stable version available
2. Version compatibility with existing dependencies
3. Any known security vulnerabilities
"""

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": feedback,
        }
    }

    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()

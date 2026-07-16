"""Git tool — safe git operations."""
import asyncio
import logging
import os
from typing import Any

import config

logger = logging.getLogger("clawd.tools.git")

# Dangerous flags that should be blocked
_BLOCKED_FLAGS = ["--force", "-f", "reset --hard", "clean -fd", "push --force"]

TOOL_DEFINITIONS = [
    {
        "name": "git",
        "description": "Run git operations safely. Supports: status, add, commit, push, pull, log, diff, branch, checkout, stash. Blocks dangerous flags like --force and reset --hard.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "add", "commit", "push", "pull", "log", "diff", "branch", "checkout", "stash"],
                    "description": "Git action to perform."
                },
                "args": {
                    "type": "string",
                    "description": "Additional arguments for the git command."
                },
                "repo_path": {
                    "type": "string",
                    "description": "Repository path. Defaults to CLAWD_HOME."
                },
                "message": {
                    "type": "string",
                    "description": "Commit message (for commit action)."
                }
            },
            "required": ["action"]
        }
    },
]


async def _git(input_data: dict) -> str:
    """Execute git operations with safety guards."""
    action = input_data["action"]
    args = input_data.get("args", "")
    repo_path = input_data.get("repo_path", str(config.CLAWD_HOME))
    message = input_data.get("message", "")

    # Safety check: block dangerous flags
    full_cmd = f"{action} {args}".lower()
    for blocked in _BLOCKED_FLAGS:
        if blocked in full_cmd:
            return f"Blocked: '{blocked}' is not allowed for safety. Use shell tool if you really need this."

    # Build git command
    if action == "commit":
        if not message:
            return "Error: 'message' required for commit action."
        cmd = f'git commit -m "{message}"'
        if args:
            cmd = f'git commit {args} -m "{message}"'
    elif action == "log":
        default_args = "--oneline -20" if not args else args
        cmd = f"git log {default_args}"
    elif action == "diff":
        cmd = f"git diff {args}" if args else "git diff"
    elif action == "branch":
        cmd = f"git branch {args}" if args else "git branch -a"
    elif action == "stash":
        cmd = f"git stash {args}" if args else "git stash list"
    else:
        cmd = f"git {action} {args}".strip()

    # Handle PAT for push operations
    env = {**os.environ, "HOME": str(config.CLAWD_HOME)}
    if action == "push":
        # Try to load PAT from .openclaw/.env.local
        env_file = config.CLAWD_HOME.parent / ".openclaw" / ".env.local"
        if env_file.exists():
            try:
                content = env_file.read_text(encoding="utf-8", errors="replace")
                for line in content.split("\n"):
                    if line.startswith("GITHUB_PAT=") or line.startswith("GH_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        env["GH_TOKEN"] = token
                        break
            except Exception as e:
                logger.debug(f"Failed to read .env file for git token: {e}")

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=repo_path,
            env=env,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)

        result_parts = []
        if stdout:
            out = stdout.decode("utf-8", errors="replace")
            if len(out) > 50_000:
                out = out[:50_000] + "\n[... truncated]"
            result_parts.append(out)
        if stderr:
            err = stderr.decode("utf-8", errors="replace")
            if len(err) > 20_000:
                err = err[:20_000] + "\n[... truncated]"
            result_parts.append(f"STDERR: {err}")
        result_parts.append(f"Exit code: {proc.returncode}")

        return "\n".join(result_parts) if result_parts else "Git command completed (no output)."

    except asyncio.TimeoutError:
        return f"Git command timed out after 60s."
    except Exception as e:
        return f"Git error: {type(e).__name__}: {e}"


TOOL_HANDLERS = {
    "git": _git,
}

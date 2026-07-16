"""File I/O tools — read, write, list directory."""
import logging
from pathlib import Path
from typing import Any

import config
from tools._base import resolve_path

logger = logging.getLogger("clawd.tools.files")

TOOL_DEFINITIONS = [
    {
        "name": "read_file",
        "description": "Read the contents of any file on the system.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path (relative to CLAWD_HOME)."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to any file. Creates parent directories if needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path (relative to CLAWD_HOME)."
                },
                "content": {
                    "type": "string",
                    "description": "Full content to write."
                },
                "append": {
                    "type": "boolean",
                    "description": "If true, append instead of overwrite. Default: false."
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_directory",
        "description": "List files and directories at a given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path. Defaults to CLAWD_HOME if empty."
                }
            },
            "required": []
        }
    },
]


async def _read_file(input_data: dict) -> str:
    path = resolve_path(input_data["path"])
    if not path.exists():
        return f"File not found: {path}"
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"Error reading {path}: {e}"
    if len(content) > 200_000:
        return content[:200_000] + f"\n\n[... truncated, {len(content)} chars total]"
    return content


MAX_WRITE_SIZE = 10 * 1024 * 1024  # 10MB

async def _write_file(input_data: dict) -> str:
    path = resolve_path(input_data["path"])

    # Size limit check
    content = input_data.get("content", "")
    if len(content) > MAX_WRITE_SIZE:
        return f"Error: Content size ({len(content):,} bytes) exceeds maximum ({MAX_WRITE_SIZE:,} bytes / 10MB)."

    path.parent.mkdir(parents=True, exist_ok=True)

    # Record file write for rollback support
    old_content = None
    if path.exists():
        try:
            old_content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.debug(f"Failed to read existing file content for rollback: {e}")
    try:
        from tools.rollback import get_tracker
        get_tracker().record_file_write(path, old_content)
    except Exception as e:
        logger.debug(f"Failed to record file write for rollback: {e}")

    mode = "a" if input_data.get("append", False) else "w"
    with open(path, mode, encoding="utf-8") as f:
        f.write(input_data["content"])
    return f"Written to {path} ({'appended' if mode == 'a' else 'created/overwritten'}), {len(input_data['content'])} chars."


async def _list_directory(input_data: dict) -> str:
    path_str = input_data.get("path", "")
    path = resolve_path(path_str) if path_str else config.CLAWD_HOME
    if not path.is_dir():
        return f"Not a directory: {path}"
    entries = sorted(path.iterdir())
    lines = []
    for e in entries[:500]:
        prefix = "[DIR]  " if e.is_dir() else "[FILE] "
        size = ""
        if e.is_file():
            s = e.stat().st_size
            size = f" ({s:,} bytes)"
        lines.append(f"{prefix}{e.name}{size}")
    result = f"Contents of {path}:\n" + "\n".join(lines)
    if len(entries) > 500:
        result += f"\n... and {len(entries) - 500} more"
    return result


TOOL_HANDLERS = {
    "read_file": _read_file,
    "write_file": _write_file,
    "list_directory": _list_directory,
}

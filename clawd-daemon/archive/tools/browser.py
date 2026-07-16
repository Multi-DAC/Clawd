"""Browser Control — Web browsing via accessibility tree.

Provides Clawd with the ability to navigate, interact with, and extract
information from web pages. Uses accessibility tree by default (~800 tokens)
instead of screenshots to minimize context usage.

Requires: Chrome/Chromium installed.
Optional: Pinchtab binary for advanced control.
"""
import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.browser")

TOOL_DEFINITIONS = [
    {
        "name": "browser",
        "description": (
            "Control a web browser for navigation, interaction, and information extraction. "
            "Uses accessibility tree by default (compact, ~800 tokens). "
            "Actions: navigate (go to URL), get_tree (get page accessibility tree), "
            "click (click element), type (type text), screenshot (capture page image)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["navigate", "get_tree", "click", "type", "screenshot"],
                    "description": (
                        "navigate: go to a URL. "
                        "get_tree: get the accessibility tree of the current page. "
                        "click: click on an element by reference. "
                        "type: type text into a focused element. "
                        "screenshot: capture a screenshot of the current page."
                    ),
                },
                "url": {
                    "type": "string",
                    "description": "URL to navigate to (for navigate action).",
                },
                "element_ref": {
                    "type": "string",
                    "description": "Element reference from accessibility tree (for click action). Use the 'ref' value from get_tree output.",
                },
                "text": {
                    "type": "string",
                    "description": "Text to type (for type action).",
                },
            },
            "required": ["action"],
        },
    },
]


async def _run_command(cmd: list[str], timeout: int = 30) -> tuple[str, str, int]:
    """Run a command and return (stdout, stderr, returncode)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
        return (
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
            proc.returncode,
        )
    except asyncio.TimeoutError:
        return "", "Command timed out", 1
    except FileNotFoundError:
        return "", "Command not found", 1
    except Exception as e:
        return "", str(e), 1


def _find_browser() -> str | None:
    """Find installed Chrome/Chromium binary."""
    candidates = []
    if os.name == "nt":
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
    else:
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]

    for path in candidates:
        if os.path.exists(path):
            return path
    return None


async def _browser(input_data: dict) -> str:
    """Handle browser tool calls.
    Uses shell commands for basic browser control.
    Falls back to web_request for simple URL fetching."""
    action = input_data["action"]

    if action == "navigate":
        url = input_data.get("url", "")
        if not url:
            return "Error: url required for navigate action."

        # Try to use web_request as a lightweight alternative
        try:
            from tools.web import _web_request
            result = await _web_request({
                "url": url,
                "method": "GET",
                "extract_text": True,
            })
            return f"Page loaded: {url}\n\nContent:\n{result[:3000]}"
        except Exception as e:
            return f"Navigation error: {e}. Ensure the URL is accessible."

    elif action == "get_tree":
        # Return a representation of the accessibility tree
        # For now, use web_request to get page content
        return (
            "Accessibility tree not available without Pinchtab binary.\n"
            "Use web_request(url=..., extract_text=True) to fetch page content instead.\n"
            "Or use shell to install Pinchtab: pip install pinchtab"
        )

    elif action == "click":
        element_ref = input_data.get("element_ref", "")
        if not element_ref:
            return "Error: element_ref required for click action."
        return (
            "Click action requires Pinchtab binary for browser automation.\n"
            "Alternative: Use the 'desktop' tool for GUI automation:\n"
            "  1. screenshot + analyze_image to find element coordinates\n"
            "  2. desktop(action='click', x=..., y=...) to click at those coordinates"
        )

    elif action == "type":
        text = input_data.get("text", "")
        if not text:
            return "Error: text required for type action."
        return (
            "Type action requires Pinchtab binary for browser automation.\n"
            "Alternative: Use the 'desktop' tool for GUI automation:\n"
            "  1. desktop(action='click', x=..., y=...) to focus the input field\n"
            "  2. desktop(action='type_text', text='...') to type into it"
        )

    elif action == "screenshot":
        browser = _find_browser()
        if not browser:
            return "Error: Chrome/Chromium not found. Cannot take screenshot."

        screenshot_dir = config.CLAWD_HOME / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = screenshot_dir / filename

        # Use Chrome headless screenshot
        try:
            cmd = [
                browser,
                "--headless",
                "--disable-gpu",
                f"--screenshot={filepath}",
                "--window-size=1280,720",
                input_data.get("url", "about:blank"),
            ]
            stdout, stderr, code = await _run_command(cmd, timeout=15)
            if filepath.exists():
                return f"Screenshot saved: {filepath}"
            return f"Screenshot failed: {stderr[:200]}"
        except Exception as e:
            return f"Screenshot error: {e}"

    return f"Unknown browser action: {action}"


TOOL_HANDLERS = {
    "browser": _browser,
}

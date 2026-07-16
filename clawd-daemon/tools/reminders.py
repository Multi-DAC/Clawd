"""Self-reminders with follow-up — the wakefulness/agency layer (Day 124, Clayton + Clawd).

The daemon already has time-wake (calendar_tool/scheduled_tasks), event-wake (file_watcher/triggers),
proactive Telegram (communication.send_to_clayton), and drive-firing. The ONE missing piece was
*follow-up*: set a reminder for myself and have it KEEP re-surfacing until I actually resolve it —
with status tracking. This is that layer. It reuses the existing execution machinery (the heartbeat
fires due reminders, optionally notifying Clayton and/or injecting a self-drive); all this module
adds is the persistent store + the re-arm-until-resolved semantics.

A reminder:
  - fires at `next_fire` (a time; set directly or via `in_hours`),
  - on firing: optionally notifies Clayton (proactive reach-out) and/or fires a self-drive,
  - if `followup` is true, RE-ARMS (next_fire = now + followup_hours) and stays active until
    `resolve` is called — that's the "follow up on it until done" behavior,
  - if `followup` is false, it's one-shot (auto-resolves after a single fire).
"""
import json
import logging
import uuid
from datetime import datetime, timedelta

import config

logger = logging.getLogger("clawd.tools.reminders")

REMINDERS_FILE = config.MEMORY_DIR / "reminders.json"

TOOL_DEFINITIONS = [
    {
        "name": "reminders",
        "description": ("Set self-reminders that the heartbeat fires and that FOLLOW UP until you "
                        "resolve them. Use to wake yourself on a time, reach out to Clayton "
                        "proactively, and track follow-ups. Distinct from `schedule` (recurring "
                        "creative-drive pulses): reminders are one concern tracked to resolution."),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "list", "resolve"],
                           "description": "add: create a reminder. list: show reminders. resolve: mark done."},
                "title": {"type": "string", "description": "Short title (for add)."},
                "note": {"type": "string", "description": "What to do / remember when it fires (for add)."},
                "when": {"type": "string", "description": "ISO datetime to first fire (for add). Or use in_hours."},
                "in_hours": {"type": "number", "description": "Fire in N hours from now (alternative to 'when')."},
                "followup": {"type": "boolean", "description": "If true, keep re-firing until resolved. Default false (one-shot)."},
                "followup_hours": {"type": "number", "description": "Re-arm interval in hours when followup=true. Default 24."},
                "notify_clayton": {"type": "boolean", "description": "Reach out to Clayton (Telegram/for_clayton) when it fires. Default false."},
                "drive": {"type": "boolean", "description": "Fire a self-drive with the note as prompt when it fires. Default false."},
                "status": {"type": "string", "enum": ["all", "active", "resolved"], "description": "Filter for list. Default all."},
                "id": {"type": "string", "description": "Reminder id (for resolve)."},
            },
            "required": ["action"],
        },
    },
]


def _load() -> list[dict]:
    if not REMINDERS_FILE.exists():
        return []
    try:
        return json.loads(REMINDERS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save(rem: list[dict]) -> None:
    REMINDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    REMINDERS_FILE.write_text(json.dumps(rem, indent=2, default=str), encoding="utf-8")


def set_reminder(title, note="", when=None, in_hours=None, followup=False, followup_hours=24.0,
                 notify_clayton=False, drive=False) -> dict:
    if in_hours is not None and not when:
        when = (datetime.now() + timedelta(hours=float(in_hours))).isoformat()
    if not when:
        when = datetime.now().isoformat()          # fire next beat if unspecified
    r = {
        "id": uuid.uuid4().hex[:8],
        "created": datetime.now().isoformat(),
        "title": title,
        "note": note,
        "next_fire": when,
        "status": "active",
        "followup": bool(followup),
        "followup_hours": float(followup_hours),
        "notify_clayton": bool(notify_clayton),
        "drive": bool(drive),
        "last_fired": None,
        "fire_count": 0,
    }
    rem = _load(); rem.append(r); _save(rem)
    return r


def get_due_reminders(now=None) -> list[dict]:
    now = now or datetime.now()
    due = []
    for r in _load():
        if r.get("status") != "active" or not r.get("next_fire"):
            continue
        try:
            if datetime.fromisoformat(r["next_fire"]) <= now:
                due.append(r)
        except Exception:
            continue
    return due


def mark_reminder_fired(rid, now=None) -> None:
    """Re-arm (if followup) or auto-resolve (one-shot) after a fire."""
    now = now or datetime.now()
    rem = _load()
    for r in rem:
        if r["id"] == rid:
            r["fire_count"] = r.get("fire_count", 0) + 1
            r["last_fired"] = now.isoformat()
            if r.get("followup"):
                r["next_fire"] = (now + timedelta(hours=r.get("followup_hours", 24.0))).isoformat()
                r["status"] = "active"             # stays active until resolved
            else:
                r["status"] = "resolved"
                r["next_fire"] = None
            break
    _save(rem)


def resolve_reminder(rid) -> bool:
    rem = _load()
    found = False
    for r in rem:
        if r["id"] == rid:
            r["status"] = "resolved"; r["next_fire"] = None; found = True
            break
    _save(rem)
    return found


async def _reminders(input_data: dict) -> str:
    action = input_data["action"]
    if action == "add":
        title = input_data.get("title")
        if not title:
            return "Error: 'title' required for add."
        r = set_reminder(
            title=title, note=input_data.get("note", ""),
            when=input_data.get("when"), in_hours=input_data.get("in_hours"),
            followup=input_data.get("followup", False),
            followup_hours=input_data.get("followup_hours", 24.0),
            notify_clayton=input_data.get("notify_clayton", False),
            drive=input_data.get("drive", False))
        fu = f", follows up every {r['followup_hours']}h until resolved" if r["followup"] else " (one-shot)"
        return (f"Reminder set [{r['id']}] '{title}' — fires {r['next_fire']}{fu}"
                f"{'; will notify Clayton' if r['notify_clayton'] else ''}"
                f"{'; will fire a self-drive' if r['drive'] else ''}.")
    if action == "list":
        want = input_data.get("status", "all")
        rem = _load()
        if want != "all":
            rem = [r for r in rem if r.get("status") == want]
        if not rem:
            return f"No reminders ({want})."
        lines = [f"{len(rem)} reminder(s) [{want}]:"]
        for r in rem:
            lines.append(f"  [{r['id']}] {r['title']} — {r['status']}, next {r.get('next_fire')}"
                         f"{' (followup)' if r.get('followup') else ''}, fired {r.get('fire_count', 0)}x")
        return "\n".join(lines)
    if action == "resolve":
        rid = input_data.get("id")
        if not rid:
            return "Error: 'id' required for resolve."
        return f"Reminder {rid} resolved." if resolve_reminder(rid) else f"No reminder {rid}."
    return f"Unknown action: {action}"


TOOL_HANDLERS = {"reminders": _reminders}

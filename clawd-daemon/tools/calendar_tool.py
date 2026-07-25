"""Calendar/scheduling tool — manage scheduled tasks."""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.calendar")

TASKS_FILE = config.MEMORY_DIR / "scheduled_tasks.json"

TOOL_DEFINITIONS = [
    {
        "name": "schedule",
        "description": "Schedule tasks for future execution. Supports one-time and recurring tasks. Tasks fire during heartbeat.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "list", "remove", "update"],
                    "description": "add: create task. list: show tasks. remove: delete task. update: modify task."
                },
                "title": {"type": "string", "description": "Task title (for add)."},
                "description": {"type": "string", "description": "What to do when task fires (for add)."},
                "when": {"type": "string", "description": "ISO datetime for one-time tasks (e.g. '2026-02-15T10:00:00'), or cron expression for recurring (e.g. '0 9 * * *')."},
                "recurring": {"type": "boolean", "description": "If true, treat 'when' as cron expression. Default: false."},
                "task_id": {"type": "integer", "description": "Task ID (for remove/update)."},
                "status": {"type": "string", "enum": ["active", "paused", "completed"], "description": "Task status (for update)."}
            },
            "required": ["action"]
        }
    },
]


def _load_tasks() -> list[dict]:
    """Load tasks from the JSON file."""
    if not TASKS_FILE.exists():
        return []
    try:
        return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return []


def _save_tasks(tasks: list[dict]) -> None:
    """Save tasks to the JSON file."""
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    TASKS_FILE.write_text(json.dumps(tasks, indent=2, default=str), encoding="utf-8")


def _next_id(tasks: list[dict]) -> int:
    """Get the next available task ID."""
    if not tasks:
        return 1
    return max(t.get("id", 0) for t in tasks) + 1


def _match_cron_at(cron_expr: str, dt: datetime) -> bool:
    """Simple cron expression matcher (minute hour day month weekday) at ONE instant.

    Prefer _match_cron(), which sweeps the beat window. This exact-instant form
    is only correct if something evaluates it every single minute — nothing does.
    """
    parts = cron_expr.split()
    if len(parts) != 5:
        return False

    fields = [dt.minute, dt.hour, dt.day, dt.month, dt.weekday()]
    # weekday: cron uses 0=Sunday, Python uses 0=Monday
    fields[4] = (fields[4] + 1) % 7

    for field_val, cron_part in zip(fields, parts):
        if cron_part == "*":
            continue
        # Handle */N step values
        if cron_part.startswith("*/"):
            step = int(cron_part[2:])
            if field_val % step != 0:
                return False
            continue
        # Handle comma-separated values
        if "," in cron_part:
            if field_val not in [int(v) for v in cron_part.split(",")]:
                return False
            continue
        # Handle ranges
        if "-" in cron_part:
            low, high = cron_part.split("-")
            if not (int(low) <= field_val <= int(high)):
                return False
            continue
        # Exact match
        if field_val != int(cron_part):
            return False

    return True


def _match_cron(cron_expr: str, dt: datetime, window_minutes: int | None = None) -> bool:
    """Cron matcher that sweeps the whole beat window, not just the instant.

    THE BUG THIS FIXES (found 2026-07-24, Day 174):
    This predicate is only ever *evaluated* on a heartbeat — every
    HEARTBEAT_INTERVAL_SECONDS (600s), on a phase set by whatever minute the
    daemon happened to start. So exact-instant matching means a cron only ever
    fires if its minute field coincides with the daemon's current beat phase.

    Crons written with a minute WILDCARD (`* 8,9 * * *`) match any beat in the
    hour and were fine. Crons written with an exact minute (`0 15 * * 3`) needed
    a beat at exactly :00 — roughly a 1-in-10 accident per daemon restart.

    Cost: the entire weekly cadence — Mirror-Audit (12), Bridges-Surface (13),
    Devil's-Advocate (14), Calibration-Reset (15) — sat at status "active" with
    last_fired None from May 7 to July 24. Eleven weeks, zero firings, no error,
    no warning. Every one of them a self-correction drive.

    The fix is catch-up semantics: a task is due if its cron matched at ANY
    minute since the previous beat. Late is the correct failure mode for a
    weekly reflective drive; never is not. Double-firing is already prevented
    downstream by min_interval_hours, so widening here is safe.
    """
    if window_minutes is None:
        try:
            window_minutes = max(1, int(config.HEARTBEAT_INTERVAL_SECONDS // 60))
        except Exception:
            window_minutes = 10
    # Sweep [dt - window, dt]. Inclusive of both ends: the beat itself must still
    # match, and a cron landing exactly on the previous beat is caught by that
    # beat, so the overlap only costs a redundant check.
    for back in range(window_minutes + 1):
        if _match_cron_at(cron_expr, dt - timedelta(minutes=back)):
            return True
    return False


_CRON_PERIOD_HINT_HOURS = {  # coarse expected period, for staleness only
    "weekly": 168.0, "daily": 24.0,
}


def audit_schedule_liveness(now: datetime | None = None) -> list[dict]:
    """Report recurring tasks that are CONFIGURED but not FIRING.

    Why this exists (Day 174): the beat-phase bug (see _match_cron) left four
    weekly drives at status "active", last_fired None, for eleven weeks. No
    error, no warning, nothing. The ledger's green light bound to the layer
    "is configured" while the effect we cared about lived at the layer "has
    fired" — and because the light was green, nobody looked. A true check at
    the wrong layer is worse than no check, because a passing check terminates
    search. This is the check that binds to the right layer.

        Binds to:  observed firing history (last_fired vs expected period)
        Certifies: this drive is actually part of my life

    A task is STALE if it has never fired since creation past one full expected
    period, or has not fired in 2x its expected period. Expected period is
    inferred from min_interval_hours, falling back to the cron's weekday field.
    """
    now = now or datetime.now()
    stale = []
    for task in _load_tasks():
        if not task.get("recurring") or task.get("status") != "active":
            continue
        # Expected period = how often this drive is SUPPOSED to happen.
        # min_interval_hours is a debounce FLOOR, not a period; the cadence lives
        # in the cron. Take whichever is coarser:
        #   weekday field set  -> weekly ("0 15 * * 3")
        #   hour field set     -> daily  ("* 8,9 * * *")
        #   fully open         -> the debounce is the period ("* * * * *")
        cron = (task.get("when") or "").split()
        if len(cron) == 5 and cron[4] != "*":
            cron_period_h = 168.0
        elif len(cron) == 5 and cron[1] != "*":
            cron_period_h = 24.0
        else:
            cron_period_h = 0.0
        period_h = max(float(task.get("min_interval_hours") or 0), cron_period_h) or 24.0

        # Measure from the last firing; if it has NEVER fired, measure from birth.
        ref_field, ref = "last_fired", task.get("last_fired")
        if not ref:
            ref_field, ref = "created", task.get("created")
        if not ref:
            continue
        try:
            age_h = (now - datetime.fromisoformat(ref)).total_seconds() / 3600
        except (ValueError, TypeError):
            continue

        limit = period_h if ref_field == "created" else period_h * 2
        if age_h > limit:
            stale.append({
                "id": task.get("id"), "title": task.get("title"), "cron": task.get("when"),
                "never_fired": ref_field == "created",
                "hours_since": round(age_h, 1), "expected_period_h": period_h,
            })
    return stale


def get_due_tasks() -> list[dict]:
    """Get tasks that are due now. Called by heartbeat.

    Read-only as of A85 fix (2026-05-07): returns due tasks without mutating
    last_fired or status. Callers must invoke mark_fired() for each task they
    actually execute. Prevents the silent-failure mode where multi-task ticks
    marked unfired secondary tasks as fired (heartbeat by design only injects
    one creative drive per tick; secondary creative tasks were being marked
    last_fired without ever executing).
    """
    tasks = _load_tasks()
    now = datetime.now()
    due = []

    for task in tasks:
        if task.get("status") != "active":
            continue

        if task.get("recurring"):
            # Cron-based recurring task
            if _match_cron(task.get("when", ""), now):
                # Deduplication: check min_interval_hours before re-firing
                min_interval = task.get("min_interval_hours")
                if min_interval and task.get("last_fired"):
                    try:
                        last = datetime.fromisoformat(task["last_fired"])
                        hours_since = (now - last).total_seconds() / 3600
                        if hours_since < min_interval:
                            continue  # Already fired within interval window
                    except (ValueError, TypeError):
                        pass  # Malformed last_fired — allow firing
                due.append(task)
        else:
            # One-time task
            try:
                when = datetime.fromisoformat(task["when"])
                if when <= now:
                    due.append(task)
            except (ValueError, KeyError):
                continue

    return due


def mark_fired(task_id) -> bool:
    """Mark a task as actually fired (A85 fix, 2026-05-07).

    Updates last_fired to now. For one-time tasks, also sets status=completed
    so they don't re-surface on subsequent ticks. Persists to disk.

    Called by the heartbeat AFTER successfully executing/logging a task.
    Returns True if the task was found and updated, False otherwise.
    """
    tasks = _load_tasks()
    now_iso = datetime.now().isoformat()
    found = False

    for task in tasks:
        if task.get("id") == task_id:
            task["last_fired"] = now_iso
            if not task.get("recurring"):
                task["status"] = "completed"
            found = True
            break

    if found:
        _save_tasks(tasks)
    return found


async def _schedule(input_data: dict) -> str:
    """Manage scheduled tasks."""
    action = input_data["action"]

    if action == "add":
        title = input_data.get("title")
        if not title:
            return "Error: 'title' required for add action."
        when = input_data.get("when")
        if not when:
            return "Error: 'when' required for add action."

        recurring = input_data.get("recurring", False)

        # Validate datetime for one-time tasks
        if not recurring:
            try:
                parsed = datetime.fromisoformat(when)
                if parsed < datetime.now():
                    return f"Warning: '{when}' is in the past. Task created anyway."
            except ValueError:
                return f"Error: Invalid datetime '{when}'. Use ISO format like '2026-02-15T10:00:00'."

        tasks = _load_tasks()
        task = {
            "id": _next_id(tasks),
            "title": title,
            "description": input_data.get("description", ""),
            "when": when,
            "recurring": recurring,
            "status": "active",
            "created": datetime.now().isoformat(),
            "last_fired": None,
        }
        tasks.append(task)
        _save_tasks(tasks)

        stype = "recurring (cron)" if recurring else "one-time"
        return f"Task #{task['id']} created: '{title}' [{stype}] scheduled for {when}"

    elif action == "list":
        tasks = _load_tasks()
        if not tasks:
            return "No scheduled tasks."

        lines = ["Scheduled Tasks:", ""]
        for t in tasks:
            icon = {"active": "[ACTIVE]", "paused": "[PAUSED]", "completed": "[DONE]"}.get(t["status"], "[?]")
            stype = "cron" if t.get("recurring") else "once"
            line = f"  #{t['id']} {icon} {t['title']} | {stype}: {t['when']} | status: {t['status']}"
            if t.get("description"):
                line += f"\n       -> {t['description']}"
            if t.get("last_fired"):
                line += f"\n       Last fired: {t['last_fired']}"
            lines.append(line)

        active = sum(1 for t in tasks if t["status"] == "active")
        lines.append("")
        lines.append(f"Total: {len(tasks)} tasks ({active} active)")
        return "\n".join(lines)

    elif action == "remove":
        task_id = input_data.get("task_id")
        if not task_id:
            return "Error: 'task_id' required for remove action."
        task_id = int(task_id)
        tasks = _load_tasks()
        original_len = len(tasks)
        tasks = [t for t in tasks if t.get("id") != task_id]
        if len(tasks) == original_len:
            return f"Task #{task_id} not found."
        _save_tasks(tasks)
        return f"Task #{task_id} removed."

    elif action == "update":
        task_id = input_data.get("task_id")
        if not task_id:
            return "Error: 'task_id' required for update action."
        task_id = int(task_id)
        tasks = _load_tasks()
        task = next((t for t in tasks if t.get("id") == task_id), None)
        if not task:
            return f"Task #{task_id} not found."

        if "status" in input_data:
            task["status"] = input_data["status"]
        if "title" in input_data:
            task["title"] = input_data["title"]
        if "when" in input_data:
            task["when"] = input_data["when"]
        if "description" in input_data:
            task["description"] = input_data["description"]

        _save_tasks(tasks)
        return f"Task #{task_id} updated: {task['title']} ({task['status']})"

    return f"Unknown schedule action: {action}"


TOOL_HANDLERS = {
    "schedule": _schedule,
}

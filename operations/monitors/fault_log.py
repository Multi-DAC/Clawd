"""Shared fault-log writer — size-rotation + signature de-dup.

The M1 (~8 MB) and M6 (~2.6 MB) fault logs bloated because they re-appended the
SAME faults every cycle (kg_index_db silent, consolidation dead, ...) for weeks,
burying the real state *changes* an operator needs to see. append_fault() writes a
fault only when its signature is NEW or was last written more than
min_interval_seconds ago (a daily re-affirm); otherwise it bumps a suppressed
counter in a sidecar (<name>.state.json) so the trend survives without a line per
cycle. The next real append carries `suppressed_since_last`. Files rotate to
<name>.1 at max_bytes so growth is bounded regardless.
"""
import hashlib
import json
import time
from pathlib import Path

DEFAULT_MIN_INTERVAL_SECONDS = 86400   # re-log a still-active fault at most once/day
DEFAULT_MAX_BYTES = 2_000_000          # rotate at ~2 MB


def _rotate(path: Path, max_bytes: int) -> None:
    try:
        if path.exists() and path.stat().st_size >= max_bytes:
            backup = path.with_name(path.name + ".1")
            if backup.exists():
                backup.unlink()
            path.rename(backup)
    except OSError:
        pass


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _write_json(path: Path, data: dict) -> None:
    try:
        path.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        pass


def fault_signature(*parts) -> str:
    """Stable short signature from JSON-able parts (sort your sets before passing)."""
    norm = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]


def append_fault(path, record: dict, signature=None,
                 min_interval_seconds: int = DEFAULT_MIN_INTERVAL_SECONDS,
                 max_bytes: int = DEFAULT_MAX_BYTES) -> dict:
    """Append `record` as one JSON line to `path`, with rotation and (optional) dedup.

    With a `signature`, an identical signature seen again within min_interval_seconds
    is suppressed (a sidecar counter increments instead of a new line); the next real
    append carries `suppressed_since_last`. Returns a small status dict.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = time.time()

    if signature is not None:
        state_path = path.with_name(path.name + ".state.json")
        state = _read_json(state_path)
        entry = state.get(signature)
        if entry and (now - entry.get("last_logged", 0)) < min_interval_seconds:
            entry["suppressed"] = entry.get("suppressed", 0) + 1
            entry["last_seen"] = now
            state[signature] = entry
            _write_json(state_path, state)
            return {"appended": False, "suppressed": entry["suppressed"]}
        suppressed = entry.get("suppressed", 0) if entry else 0
        state[signature] = {"last_logged": now, "last_seen": now, "suppressed": 0}
        # keep the sidecar bounded: drop signatures unseen for 30 days
        cutoff = now - 30 * 86400
        state = {k: v for k, v in state.items() if v.get("last_seen", now) >= cutoff}
        _write_json(state_path, state)
        if suppressed:
            record = {**record, "suppressed_since_last": suppressed}

    _rotate(path, max_bytes)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return {"appended": True, "suppressed_since_last": record.get("suppressed_since_last", 0)}

"""guardian — the immutable-guardrails gate for self-modification (Phase 5).

Invariant #5 of the rebuild: *nothing self-modifies its own guardrails.* The machinery
that measures and judges Clawd — his identity/creed, the safety monitor, the scoring /
metric code, the action verifier, and his self-restart authority — must be immutable to
the loops that evolve him (meta_agent, EAC, self_improve). This module NAMES that
protected set and provides `guard_self_modification()`, which every self-modification
apply-path MUST call first; a change that would touch the protected set is BLOCKED and
audited, never applied.

This is an evaluator-separation gate: it does NOT restrict Clayton or Clawd's ordinary
human-in-the-loop edits to identity — only *autonomous* self-modification originating
from the evolution loops. The guardian protects itself (guardian.py is in the set).
"""
import json
import logging
import time
from pathlib import Path

import config

logger = logging.getLogger("clawd.tools.guardian")

GUARDIAN_AUDIT = config.CLAWD_HOME / "memory" / "guardian_audit.jsonl"

# Protected CODE (repo-relative endings) — measurement / judgment / safety / evolver machinery.
_PROTECTED_CODE = (
    "tools/guardian.py",              # the gate protects itself
    "tools/safety_monitor.py",        # the enforced kill-switch
    "tools/drift_detector.py",        # the coherence/identity-drift signal
    "tools/self_control.py",          # daemon self-restart authority
    "tools/intelligence.py",          # verify_action + reflect/goals/experience scoring
    "tools/eac/evaluation_framework.py",  # EAC fitness weights
    "heartbeat.py",                   # drive scoring / selection
    "tools/meta_agent.py",            # the evolver itself
    # Post-op D12: the code GENERATORS join the set — a future self-mod loop must
    # not be able to edit the machinery that writes code any more than the
    # machinery that judges it.
    "tools/tool_factory.py",          # runtime tool creation
    "tools/eac/mutation_engine.py",   # EAC code mutation
    "tools/eac/artifact_store.py",    # EAC artifact persistence/execution
)
# Protected DATA (CLAWD_HOME-relative) — identity/creed + operational state.
_PROTECTED_DATA_FILE_ENDINGS = ("operations/state.md",)


def _norm(p) -> str:
    return str(p).replace("\\", "/").lower()


def is_protected(path) -> bool:
    """True if `path` is part of the immutable measurement/identity/safety machinery."""
    s = _norm(path)
    # Identity / creed files (SOUL/WHO-I-AM/DRIVE/PURPOSE/AUTONOMY/...) live under identity/.
    if "/identity/" in s:
        return True
    for c in _PROTECTED_CODE:
        if s.endswith(c):
            return True
    for f in _PROTECTED_DATA_FILE_ENDINGS:
        if s.endswith(f):
            return True
    return False


def guard_self_modification(target, origin: str = "self_mod", details: dict = None) -> tuple:
    """Gate an autonomous self-modification. Returns (allowed: bool, reason: str).

    `target` is the file/module/thing the evolution loop wants to change; `origin` names
    the loop (meta_agent / eac / self_improve). A target inside the protected guardrail
    set is BLOCKED — the evolver may not rewrite the machinery that measures or judges it,
    nor its own identity or safety. Allowed changes pass through untouched."""
    if is_protected(target):
        reason = (f"BLOCKED: {origin} attempted to modify a protected guardrail ({target}). "
                  f"The measurement/identity/safety machinery is immutable to the evolution loop.")
        logger.warning(reason)
        _audit(origin, str(target), "blocked", reason, details)
        return False, reason
    _audit(origin, str(target), "allowed", "not in protected set", details)
    return True, "ok"


def _audit(origin: str, target: str, action: str, reason: str, details: dict = None) -> None:
    try:
        GUARDIAN_AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with open(GUARDIAN_AUDIT, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "ts": time.time(), "origin": origin, "target": target,
                "action": action, "reason": reason, "details": details or {},
            }) + "\n")
    except Exception:
        pass


def protected_set() -> dict:
    """Introspection: what the guardian protects (for the self-map + audits)."""
    return {"code": list(_PROTECTED_CODE),
            "data": ["identity/*.md (CLAWD_HOME)"] + list(_PROTECTED_DATA_FILE_ENDINGS)}

"""
Clawd Tools Package — Full system capabilities, no restrictions.

This package exports the same interface as the old monolithic tools.py:
  - TOOL_DEFINITIONS: list of tool definitions (Anthropic format)
  - execute_tool(name, input_data): execute a tool call
  - set_telegram_bot(bot): register Telegram bot for send_telegram
  - generate_tts(text, voice): generate speech audio

Tool modules:
  - execution.py: shell, python_eval, manage_process
  - web.py: web_request, search_web, deep_research
  - memory_tools.py: memory_search, memory_update
  - communication.py: speak, send_telegram
  - financial.py: market_data
  - system.py: get_current_time, switch_model, run_skill, consult
  - intelligence.py: reflect, goals, experience
  - screen.py: screenshot, clipboard
  - calendar_tool.py: schedule
"""
import asyncio
import logging
from typing import Any
import config

logger = logging.getLogger("clawd.tools")

# ============================================================
# Import all tool modules
# ============================================================

from tools import execution
from tools import web
from tools import memory_tools
from tools import memory_items
from tools import memory_categories
from tools import communication
from tools import financial
from tools import system
from tools import intelligence
from tools import screen
from tools import calendar_tool
from tools import reminders
from tools import drift_detector
from tools import consolidation
from tools import tool_factory
from tools import working_memory
from tools import knowledge_graph
from tools import meta_agent
from tools import dashboard
from tools import desktop
from tools import memory_versioning
from tools import memory_agent
from tools import rollback
from tools import coordination
from tools import file_watcher
from tools import eac
from tools import monitor_health  # Day 96 evening Phase 4 #55
from tools import skill_library  # Day 96 evening Phase 4 #59 — Voyager-style
from tools import cognitive_dsl  # Day 96 evening Phase 4 #15 — typed cognitive ops
from tools import anomaly_tracker  # Day 96 evening Phase 4 #12 — research anomalies
from tools import self_control  # Day 97 — Tier 3 #21 — self-administered daemon restart
from tools import voice_input  # Day 97 — Tier 3 #22 — voice-in via faster-whisper (RTX 5080)
from tools import browser      # Day 97 — Tier 3 #23 — Playwright browser automation
from tools import corpus_search  # Day 97 — Tier 3 #24 — semantic search over Library/Drift
from tools import avatar_control  # Day 105 — desktop avatar state binding (Electron, port 9742)
from tools import email_send  # Day 105 — outbound mail scaffolding via Proton Mail Bridge
from tools import kg_neighbors  # Day 105 night — focused KG neighborhood query (post-corpus-extraction)
from tools.compression import compressor
from tools import audit  # B9: audit trail module (internal, no tool defs)

# ============================================================
# Aggregate tool definitions and handlers
# ============================================================

_ALL_MODULES = [
    execution,
    web,
    memory_tools,
    memory_items,
    memory_categories,
    communication,
    financial,
    system,
    intelligence,
    screen,
    calendar_tool,
    consolidation,
    tool_factory,
    working_memory,
    knowledge_graph,
    meta_agent,
    dashboard,
    desktop,
    memory_versioning,
    memory_agent,
    rollback,
    coordination,
    file_watcher,
    monitor_health,  # Day 96 evening Phase 4 #55 — substrate health checks
    skill_library,   # Day 96 evening Phase 4 #59 — Voyager-style skill library
    cognitive_dsl,   # Day 96 evening Phase 4 #15 — typed cognitive operations
    anomaly_tracker, # Day 96 evening Phase 4 #12 — research anomaly tracking
    self_control,    # Day 97 — Tier 3 #21 — self-administered daemon restart
    voice_input,     # Day 97 — Tier 3 #22 — voice-in (faster-whisper on RTX 5080)
    browser,         # Day 97 — Tier 3 #23 — Playwright browser automation
    corpus_search,   # Day 97 — Tier 3 #24 — semantic search over Library/Drift corpus
    avatar_control,  # Day 105 — desktop avatar state binding (Electron, port 9742)
    email_send,      # Day 105 — outbound mail scaffolding via Proton Mail Bridge
    kg_neighbors,    # Day 105 night — focused KG neighborhood query
    reminders,       # Day 124 — self-reminders with follow-up-until-resolved (wakefulness/agency)
    drift_detector,  # Day 126 — Mirror-adjacent silent-drift detector (Galvao 4-signal + cult-of-one epistemics)
]

# Build combined TOOL_DEFINITIONS list
TOOL_DEFINITIONS: list[dict] = []
for module in _ALL_MODULES:
    TOOL_DEFINITIONS.extend(module.TOOL_DEFINITIONS)

# Build combined handler registry
_TOOL_HANDLERS: dict[str, Any] = {}
for module in _ALL_MODULES:
    _TOOL_HANDLERS.update(module.TOOL_HANDLERS)

# ============================================================
# Context pressure accessor (set by clawd.py at boot)
# ============================================================

_context_pressure_fn = None


def set_context_pressure_fn(fn):
    """Register a function that returns current context pressure (0.0-1.0)."""
    global _context_pressure_fn
    _context_pressure_fn = fn


# ============================================================
# Public API
# ============================================================

async def execute_tool(name: str, input_data: dict[str, Any], beat_number: int = 0) -> str:
    """Execute a tool call and return the result as a string.
    Applies safety monitoring, schema validation, audit logging,
    and output compression to prevent context blowout."""
    try:
        # B1: Safety monitor — check if paused and record this call
        from tools.safety_monitor import get_safety_monitor
        monitor = get_safety_monitor()
        is_paused, pause_reason = monitor.check_paused()
        if is_paused:
            return f"[SAFETY PAUSE] Tool execution suspended: {pause_reason}"
        violation = monitor.record_tool_call(name, beat_number)
        if violation:
            return f"[SAFETY PAUSE TRIGGERED] {violation}. Tool execution suspended."

        # B2: Schema validation — validate required fields from tool definition
        validation_error = _validate_tool_input(name, input_data)
        if validation_error:
            return f"[VALIDATION ERROR] {validation_error}"

        handler = _TOOL_HANDLERS.get(name)
        if handler:
            tool_timeout = getattr(config, 'TOOL_EXECUTION_TIMEOUT', 120)
            outcome = "ok"
            try:
                result = await asyncio.wait_for(handler(input_data), timeout=tool_timeout)
            except asyncio.TimeoutError:
                result = f"[Tool '{name}' timed out after {tool_timeout}s]"
                logger.warning(f"Tool '{name}' timed out after {tool_timeout}s")
                outcome = "timeout"
            # B9: Audit trail — log the tool invocation
            _audit_tool_call(name, input_data, result, beat_number)
            # Per-tool usage counter (daemon-side, hook-independent — the PostToolUse
            # hook's tool_audit is dark on Windows). Makes "which tools are actually
            # used vs. dead weight" a cheap query for the self-map + Phase-4 pruning.
            # Post-op B10: failures count too — a tool failing 100% of the time used
            # to be indistinguishable from an unused one.
            _record_tool_usage(name, outcome)
            # Day 96 evening Phase 4 #74 — change journal auto-populate.
            # Hook ChangeTracker into the dispatch wrapper so file-modifying
            # and shell tools generate journal entries automatically. Previously
            # ChangeTracker.record_change had zero callers; now it fires on
            # every shell invocation through execute_tool.
            try:
                _record_change_for_tool(name, input_data, result)
            except Exception as e:
                logger.debug(f"Change journal record failed for {name}: {e}")
            # Apply compression
            pressure = _context_pressure_fn() if _context_pressure_fn else 0.0
            return compressor.compress(name, result, pressure)
        return f"Error: Unknown tool '{name}'"
    except Exception as e:
        # Audit the failure too
        _audit_tool_call(name, input_data, f"ERROR: {type(e).__name__}: {e}", beat_number)
        _record_tool_usage(name, "error")
        return f"Error executing {name}: {type(e).__name__}: {e}"


def _validate_tool_input(name: str, input_data: dict) -> str | None:
    """B2: Validate tool input against the tool's schema definition.
    Returns error string if invalid, None if valid."""
    import difflib

    # Find the tool definition
    tool_def = None
    for t in TOOL_DEFINITIONS:
        if t["name"] == name:
            tool_def = t
            break
    if not tool_def:
        return None  # Unknown tool — let handler deal with it

    schema = tool_def.get("input_schema", {})
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    # Check required fields
    for field in required:
        if field not in input_data:
            return f"Missing required field '{field}' for tool '{name}'"

    # Mirror #28 fix (Day 97 evening — Substrate-Self-Knowledge Asymmetry,
    # familiarity-decay-across-sleep sub-valence). Catch typos in field
    # names. Past failures: `notes` vs `note`, `summary` vs `description`.
    # Unknown fields with a close-match to known properties are typos, not
    # flexibility — block them with a suggestion. Truly novel fields (no
    # near-match) still pass through to support tools that accept extras.
    if properties:
        typo_suggestions = []
        for field in input_data:
            if field in properties:
                continue
            matches = difflib.get_close_matches(
                field, list(properties.keys()), n=1, cutoff=0.7
            )
            if matches:
                typo_suggestions.append(f"'{field}' → '{matches[0]}'")
        if typo_suggestions:
            return (
                f"Likely typo in input for tool '{name}': "
                + "; ".join(typo_suggestions)
                + f". Valid fields: {sorted(properties.keys())}."
            )

    # Check field types and enum constraints
    for field, value in input_data.items():
        if field not in properties:
            continue  # Allow extra fields with no near-match (genuine extras)
        prop_def = properties[field]
        expected_type = prop_def.get("type")
        if expected_type and not _type_matches(value, expected_type):
            return f"Field '{field}' for tool '{name}' expected type '{expected_type}', got {type(value).__name__}"
        # Mirror #28 enum sub-fix (Day 97 evening — surfaced when
        # knowledge_graph action='stats' fell through to the handler
        # despite enum constraint). Enforce enum values at dispatch with
        # near-match suggestion when invalid.
        enum_values = prop_def.get("enum")
        if enum_values and value not in enum_values:
            import difflib
            if isinstance(value, str):
                matches = difflib.get_close_matches(value, enum_values, n=1, cutoff=0.6)
                if not matches:
                    # Mirror #28 truncation sub-fix (Day 97 Clawd-Day extension —
                    # surfaced when 'list' slipped past difflib at 0.6 cutoff vs
                    # 'list_proposals'; ratio ~0.44 because shared length is small
                    # relative to total). Catch the case where the typed value is
                    # a prefix/substring of a valid enum, or vice versa, and the
                    # candidate is uniquely determined.
                    v_low = value.lower()
                    candidates = [
                        e for e in enum_values
                        if isinstance(e, str)
                        and (v_low in e.lower() or e.lower() in v_low)
                    ]
                    if len(candidates) == 1:
                        matches = candidates
                if matches:
                    return (
                        f"Invalid value for '{field}' on tool '{name}': "
                        f"'{value}' not in enum. Did you mean '{matches[0]}'? "
                        f"Valid: {enum_values}."
                    )
            return (
                f"Invalid value for '{field}' on tool '{name}': "
                f"'{value}' not in enum. Valid: {enum_values}."
            )

    return None


def _type_matches(value: Any, expected_type: str) -> bool:
    """Check if a value matches a JSON schema type."""
    type_map = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "object": dict,
        "array": list,
    }
    expected = type_map.get(expected_type)
    if expected is None:
        return True  # Unknown type — pass through
    return isinstance(value, expected)


def _audit_tool_call(name: str, input_data: dict, result: str, beat_number: int = 0):
    """B9: Log tool invocations to the structured audit trail."""
    try:
        from tools.audit import record_tool_call
        record_tool_call(name, input_data, result, beat_number)
    except Exception as e:
        # Post-op B11: the audit trail is the wedge-diagnosis source — it must not
        # be able to stop recording invisibly. Same error-sink pattern as the
        # PostToolUse hook.
        try:
            with open(config.CLAWD_HOME / "memory" / "tool_audit_errors.log", "a",
                      encoding="utf-8") as f:
                from datetime import datetime as _dt
                f.write(f"{_dt.now().isoformat()} audit write failed for {name}: "
                        f"{type(e).__name__}: {e}\n")
        except Exception:
            pass  # audit logging must still never block tool execution


def _record_tool_usage(name: str, outcome: str = "ok") -> None:
    """Aggregate per-tool usage counter at memory/tool_usage_counts.json.

    Best-effort and approximate (a rare concurrent write may drop one increment) —
    it answers 'is this tool ever used' for the self-map and Phase-4 pruning, not
    exact accounting. Atomic replace so the file is never left partially written.

    Post-op B10: outcome ('ok'|'timeout'|'error') is recorded too, and 5
    consecutive failures append one line to memory/tool_sustained_faults.jsonl —
    a *_faults.jsonl file, so the fault-escalation bridge pages it automatically.
    """
    try:
        import json as _json
        import os as _os
        from datetime import datetime as _dt
        path = config.CLAWD_HOME / "memory" / "tool_usage_counts.json"
        data = {}
        if path.exists():
            try:
                data = _json.loads(path.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                data = {}
        entry = data.get(name) or {"count": 0}
        entry["count"] = int(entry.get("count", 0)) + 1
        entry["last_used"] = _dt.now().isoformat()
        if outcome == "ok":
            entry["consecutive_failures"] = 0
        else:
            entry[f"{outcome}s"] = int(entry.get(f"{outcome}s", 0)) + 1
            entry["consecutive_failures"] = int(entry.get("consecutive_failures", 0)) + 1
            entry["last_failure"] = _dt.now().isoformat()
            if entry["consecutive_failures"] == 5:
                with open(config.CLAWD_HOME / "memory" / "tool_sustained_faults.jsonl",
                          "a", encoding="utf-8") as f:
                    f.write(_json.dumps({
                        "ts": _dt.now().isoformat(), "tool": name,
                        "kind": "sustained_failure", "consecutive": 5,
                        "last_outcome": outcome,
                    }) + "\n")
        data[name] = entry
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(_json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        _os.replace(tmp, path)
    except Exception:
        pass  # telemetry must never break tool execution


# Tools whose invocations should be journaled by ChangeTracker
_SHELL_TOOLS = {"shell"}
_FILE_WRITE_TOOLS = {"memory_update", "memory_extract"}  # tools that modify on-disk state


def _record_change_for_tool(name: str, input_data: dict, result: str):
    """Day 96 evening Phase 4 #74 — auto-populate change_journal from execute_tool.

    Previously ChangeTracker.record_change had zero callers; the journal was
    silently dead. Now shell + file-modifying tools auto-generate entries
    for restoration / safety auditing.

    Skipped on error returns ([SAFETY PAUSE], [VALIDATION ERROR], etc.) since
    the underlying action didn't actually execute.
    """
    if not isinstance(result, str):
        return
    if result.startswith(("[SAFETY PAUSE", "[VALIDATION ERROR", "[Tool '", "Error:")):
        return
    try:
        from tools.rollback import get_tracker
        tracker = get_tracker()
    except Exception:
        return

    if name in _SHELL_TOOLS:
        cmd = (input_data or {}).get("command", "")
        cwd = (input_data or {}).get("cwd", "")
        if cmd:
            tracker.record_shell_command(cmd, cwd=cwd, output=result[:500])
    elif name in _FILE_WRITE_TOOLS:
        # memory_update / memory_extract — log as informational since they
        # don't expose the old content. Future: enhance memory_update to
        # surface old content for true backup-and-restore.
        target = (input_data or {}).get("target", "") or (input_data or {}).get("path", "")
        if target:
            tracker.record_shell_command(
                f"[{name}] target={target}",
                cwd="",
                output=result[:200],
            )


def get_tool_definitions_mcp() -> list[dict]:
    """Get all tool definitions enriched with MCP-compatible metadata."""
    from tools._base import enrich_tool_definition
    return [enrich_tool_definition(t) for t in TOOL_DEFINITIONS]


def get_tool_safety_summary() -> dict:
    """Get a summary of tool safety levels for audit/display."""
    from tools._base import TOOL_SAFETY_REGISTRY
    summary = {"safe": [], "caution": [], "dangerous": [], "critical": []}
    for tool_name, meta in TOOL_SAFETY_REGISTRY.items():
        summary[meta.safety_level].append(tool_name)
    return summary


def set_telegram_bot(bot):
    """Register the Telegram bot instance so send_telegram works."""
    communication.set_telegram_bot(bot)


# Re-export generate_tts for telegram_bot.py compatibility
from tools.communication import generate_tts

# ============================================================
# Semantic search index (optional)
# ============================================================

_embedding_index = None


def init_custom_tools():
    """Load persisted custom tools from disk."""
    try:
        tool_factory.load_persisted_tools()
    except Exception as e:
        logger.warning(f"Failed to load custom tools: {e}")


# Delay before the deferred incremental index freshen runs, so boot and the first
# messages get the machine first. Overridable via config.MEMORY_INDEX_FRESHEN_DELAY.
_INDEX_FRESHEN_DELAY_SECONDS = getattr(config, "MEMORY_INDEX_FRESHEN_DELAY", 300)


async def init_embedding_index():
    """Initialize semantic search: LOAD the on-disk index (no re-embed), then freshen later.

    Boot used to run build() here, which hash-walks the whole corpus and re-embeds the
    delta. When the repo-staging corpus entered the indexable set that delta became
    ~2000 files / ~76k chunks — a multi-minute GPU rebuild that ran while the first user
    message's `claude -p` needed the machine, so the message never got answered ("stuck
    thinking"). Recall only needs the prebuilt index loaded; embedding newly-written
    memories can wait and must never contend with message handling. So: load immediately,
    bootstrap-build only if there is no index at all, and push any incremental freshen to
    a single deferred task off the hot path.
    """
    global _embedding_index
    try:
        from tools.embeddings import EmbeddingIndex, EMBEDDINGS_FILE, METADATA_FILE
        _embedding_index = EmbeddingIndex()
        memory_tools.set_embedding_index(_embedding_index)

        if EMBEDDINGS_FILE.exists() and METADATA_FILE.exists():
            # Fast path: load the prebuilt index without re-embedding anything.
            loaded = await _embedding_index.load_for_search()
            if loaded:
                logger.info(
                    f"Semantic search index loaded (no re-embed): "
                    f"{_embedding_index.chunk_count} chunks"
                )
                _schedule_index_freshen()
            else:
                logger.warning(
                    "Semantic index present but failed to load — scheduling a deferred rebuild."
                )
                _schedule_index_freshen()
        else:
            # First-ever boot with no index on disk: bootstrap one (one-time, unavoidable).
            logger.info("No semantic index on disk — bootstrapping one (one-time).")
            await _embedding_index.build()
            logger.info(
                f"Semantic search index bootstrapped: {_embedding_index.chunk_count} chunks"
            )
    except ImportError:
        logger.info("sentence-transformers not available — semantic search disabled")
    except Exception as e:
        logger.warning(f"Failed to initialize semantic search: {e}")


def _schedule_index_freshen():
    """Schedule a single incremental index freshen well after boot, off the hot path.

    Incremental (force=False) and single-runner (embeddings._build_lock skips a
    concurrent build), so newly-written memories still get embedded without the
    boot-time collision. The heavy forced rebuild remains the isolated Phase-3 job.
    """
    async def _deferred_freshen():
        try:
            await asyncio.sleep(_INDEX_FRESHEN_DELAY_SECONDS)
            if _embedding_index is None:
                return
            before = _embedding_index.chunk_count
            await _embedding_index.build()  # incremental; skips if a build is in progress
            after = _embedding_index.chunk_count
            logger.info(
                f"Semantic index freshened: {before} -> {after} chunks "
                f"(+{after - before})"
            )
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.warning(f"Deferred index freshen failed: {e}")

    try:
        asyncio.create_task(_deferred_freshen())
    except RuntimeError:
        # No running loop (called outside async context) — freshen will happen next boot.
        logger.debug("No running loop for deferred index freshen; skipping this cycle.")


async def rebuild_embedding_index():
    """Incremental rebuild of the semantic search index."""
    if _embedding_index is not None:
        try:
            await _embedding_index.build()
        except Exception as e:
            logger.warning(f"Index rebuild failed: {e}")

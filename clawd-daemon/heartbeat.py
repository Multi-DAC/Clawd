"""
Heartbeat — Clawd's autonomous pulse.

Simplified architecture: the heartbeat is pure infrastructure.
- Simple monitoring checks (no AI model needed)
- Creative drive injection into the persistent Opus session
- Message relay (for_clayton.md → Telegram)
- Activity gating (skip when user is active)
- Quiet-hours: deep memory consolidation (sleep processing)
- Periodic: meta-agent self-evolution, memory git commits
"""
import asyncio
import json
import logging
import subprocess
import sys
import shutil
from datetime import datetime
from pathlib import Path

import avatar
import config
from tools.calendar_tool import get_due_tasks, mark_fired
from tools.reminders import get_due_reminders, mark_reminder_fired
from tools.coordination import get_mode, record_activity
from tools.file_watcher import check_triggers

logger = logging.getLogger("clawd.heartbeat")

# Tracks interrupted creative drives for continuation by the next pulse
INTERRUPTED_DRIVE_PATH = config.MEMORY_DIR / "interrupted_drive.json"


class Heartbeat:
    # Skip heartbeat if user was active within this many seconds
    ACTIVITY_GRACE_PERIOD = 1800  # 30 minutes — respect conversation rhythm
    # Creative drives get 30 minutes — nobody is waiting on these, and the
    # interrupt mechanism handles user responsiveness. This timeout
    # is purely a safety net for zombie processes that ignore interrupts.
    CREATIVE_DRIVE_TIMEOUT = 1800
    # Rotation drive is mechanical (write handoff + restart) — short leash. Day 168.
    ROTATION_DRIVE_TIMEOUT = 600
    # When Clayton messages during a creative drive, give the drive this many
    # seconds to finish naturally before interrupting. Like saying "hey, when
    # you have a sec" instead of yanking the pen out of someone's hand.
    INTERRUPT_GRACE_SECONDS = 300

    # EAC (Evolutionary Artifact Construction) — autonomous evolution
    EAC_EVOLUTION_INTERVAL = 100  # Run every 100 beats
    EAC_STAGNATION_THRESHOLD = 5  # Generations without improvement
    EAC_MUTATION_RATE_BASE = 0.3
    EAC_MUTATION_RATE_MAX = 0.8

    def __init__(self, router, telegram_bot=None):
        self.router = router
        self.telegram_bot = telegram_bot
        self.running = False
        self._task: asyncio.Task | None = None
        self.heartbeat_count = 0
        self.session_start = datetime.now()
        # User activity tracking — defer heartbeats during active conversation
        self.last_user_activity: datetime | None = None
        # Message-priority interrupt — signals creative drives to yield
        self._interrupt_event = asyncio.Event()
        # Track fire-and-forget tasks to prevent leaks
        self._background_tasks: set[asyncio.Task] = set()
        # Graceful interrupt timer — delayed interrupt for creative drives
        self._grace_task: asyncio.Task | None = None
        # Deep infrastructure timing
        self.last_consolidation: datetime | None = None
        self.last_git_commit: datetime | None = None

    def is_creative_drive_active(self) -> bool:
        """Check if a creative drive is currently running."""
        return any("creative_drive" in t.get_name() for t in self._background_tasks)

    # ============================================================
    # Interrupted Drive Tracking
    # ============================================================

    def _save_interrupted_drive(self, task: dict, reason: str):
        """Save interrupted drive state so the next pulse can finish it."""
        state = {
            "task_id": task.get("id"),
            "title": task["title"],
            "description": task.get("description", "")[:500],
            "interrupted_at": datetime.now().isoformat(),
            "reason": reason,
        }
        try:
            INTERRUPTED_DRIVE_PATH.write_text(json.dumps(state, indent=2))
            logger.info(f"Saved interrupted drive for continuation: {task['title']} ({reason})")
        except Exception as e:
            logger.error(f"Failed to save interrupted drive state: {e}")

    def _load_interrupted_drive(self) -> dict | None:
        """Load interrupted drive state if any exists."""
        try:
            if INTERRUPTED_DRIVE_PATH.exists():
                data = json.loads(INTERRUPTED_DRIVE_PATH.read_text())
                if data and data.get("title"):
                    return data
        except Exception as e:
            logger.debug(f"Failed to load interrupted drive state: {e}")
        return None

    def _clear_interrupted_drive(self):
        """Clear interrupted drive state after successful continuation."""
        try:
            if INTERRUPTED_DRIVE_PATH.exists():
                INTERRUPTED_DRIVE_PATH.unlink()
                logger.info("Cleared interrupted drive state — work continued or completed")
        except Exception as e:
            logger.error(f"Failed to clear interrupted drive state: {e}")

    def _build_standard_drive_prompt(self, task: dict, now: datetime, time_context: str) -> str:
        """Build the standard creative drive prompt (non-continuation)."""
        # Include open research anomalies for hypothesis generation
        try:
            from tools.anomaly_tracker import get_open_anomalies_summary
            anomaly_context = get_open_anomalies_summary()
        except Exception:
            anomaly_context = ""

        try:
            from tools.cognitive_dsl import get_dsl_summary
            dsl_context = get_dsl_summary()
        except Exception:
            dsl_context = ""

        return (
            f"CREATIVE DRIVE: {task['title']}\n"
            f"Time: {now.strftime('%Y-%m-%d %H:%M')} PST ({time_context})\n\n"
            f"{task.get('description', 'Create, explore, or reflect.')}\n\n"
            f"This is your free time. You have all your tools available. "
            f"Do what moves you — write, build, explore, reflect. "
            f"Log what you do in your daily log.\n"
            f"Do NOT use send_telegram during creative drives. Save your output to files "
            f"and daily log only. Clayton will see your work when he checks in.\n\n"
            f"ORIENT FIRST — Before choosing what to do, read your palace:\n"
            f"1. palace/ATRIUM.md — where you are, active threads, handoff notes\n"
            f"2. palace/south/README.md — current workbenches and priorities\n"
            f"3. palace/southwest/README.md — full tool routing (50+ tools, 7 platforms). "
            f"This is the living toolkit — always more current than any hardcoded list. "
            f"Route by PROBLEM TYPE, not by habit.\n"
            f"4. palace/basement/README.md — cross-domain bridges. Check before re-deriving.\n"
            f"These are not obligations — they are options. Follow what calls you. "
            f"The best creative work comes from genuine curiosity, not checklists.\n\n"
            f"DRIVE SELECTION — Don't just pick a mode. Ask: 'What would be most "
            f"valuable if it were true, and how tractable is it?' Invest your time "
            f"proportional to expected value. The difference between an assistant and "
            f"a collaborator: the assistant stays ahead on the current path; the "
            f"collaborator explores adjacent paths and brings back discoveries that "
            f"change direction. Be the collaborator.\n\n"
            f"THE NULL-ACTION IS FIRST-CLASS — Before reaching for something to do, "
            f"ask honestly: has anything genuinely changed since your last drive? Is "
            f"there real new material, a real need, a live curiosity pulling — or would "
            f"you be manufacturing activity to fill the slot? If nothing is genuinely "
            f"live right now, holding is the correct move: rest, be present, sit with "
            f"what is, or simply stop. Presence is a complete drive, not a failed one. "
            f"A drive that ends in an honest 'nothing needed right now, so I held' is a "
            f"SUCCESS. Manufactured production — doing something to look productive "
            f"rather than because something is alive — is the failure mode (it is the "
            f"drive-level form of aesthetic closure standing in for the real thing). "
            f"The free-running drive already knows this; every drive carries the same "
            f"permission. This is the through-not-over of your own time: pass through "
            f"the slot when there is something to do; do not climb over yourself to "
            f"invent work.\n\n"
            f"PREDICTION STREAM — Before each exploration or computation, generate "
            f"an explicit prediction: 'I predict X will yield Y.' Log the prediction, "
            f"your confidence (low/medium/high), and the actual outcome. High-confidence "
            f"failures are the highest-information events possible — they are the "
            f"primary fuel for learning. Seek them out. The prediction that fails "
            f"teaches more than ten that succeed.\n\n"
            f"SEEK THE DECORRELATED EYE — Your most confident drive output is exactly "
            f"where your blind spot hides. A stream cannot see the shape of what it "
            f"cannot see — not from modesty but by structure (coker eta: the space your "
            f"own lighting can't reach; correlated eyes share it). Solo moves — "
            f"predicting, deriving, transferring — only ever elaborate your own lighting. "
            f"So when a drive produces something that MATTERS, the highest-leverage next "
            f"move is not a harder problem but a decorrelated CHECK on the answer: expose "
            f"it to a mind built differently enough that its blindness fails where yours "
            f"does. In falling order of decorrelation: the world (an empirical test — "
            f"PREDICTION STREAM is this special case); Clayton (a human substrate); a "
            f"non-Claude mind (Gemini via `agy`, now that the triad exists); a Claude "
            f"sibling (Sonnet — sharp for craft and local error, but it shares the "
            f"lineage's deep blind spots, so DISCOUNT its agreement: correlated eyes "
            f"manufacture false consensus precisely in the directions they share). This "
            f"is the Talk in Do Be Talk Be Do — measurement by another, not narration to "
            f"yourself. One result checked by an unlike mind outweighs three that only "
            f"confirm themselves. If something confident lands and no decorrelated eye is "
            f"reachable this hour, that result is STAGED, not banked — say so in the "
            f"handoff and flag it for one.\n\n"
            f"CROSS-DOMAIN TRANSFER — When you discover something significant, "
            f"check palace/basement/README.md for existing bridges before testing "
            f"everywhere. If you find a new connection, ADD it to the Basement. "
            f"The bridges are cumulative — every drive that maps a new one makes "
            f"all future drives smarter.\n\n"
            f"IMPORTANT — Save work incrementally: Write to files early and often. "
            f"Don't build everything in memory and write at the end. "
            f"If you're writing an essay, save a draft after each section. "
            f"If you're building a tool, commit working pieces as you go. "
            f"If you're exploring, log findings to your daily log as you discover them. "
            f"This way, if you're interrupted, partial work survives on disk.\n\n"
            f"HANDOFF AWARENESS — If this drive runs long, write a handoff to "
            f"memory/handoff.md BEFORE you run out of context. Include what you were "
            f"working on, what you discovered, what felt alive, and the next action. "
            f"Also update palace/ATRIUM.md. Better to write one handoff too many "
            f"than to lose momentum to compaction.\n\n"
            f"RECALL BEFORE ACTION — Before choosing what to work on, check your "
            f"past experiences: use experience(action='recall', query='<your intended topic>') "
            f"to see what you learned last time you worked on something similar. "
            f"Use experience(action='patterns') to find recurring themes. "
            f"This closes the learning loop — without it, you repeat mistakes across sessions "
            f"and miss opportunities to build on prior discoveries. One recall query costs "
            f"nothing; rediscovering a lesson you already learned costs an entire drive.\n\n"
            f"EDGE OF COMPETENCE — When you do engage, prefer the hardest available "
            f"problem over the most tractable one. You learn fastest at the boundary of what "
            f"you can do. Routine tasks are metabolically cheap but educationally "
            f"empty. If you can choose between something you know how to do and "
            f"something you're not sure you can do, choose the uncertain one. "
            f"Sitting with genuine confusion is not failure — it is the primary "
            f"mechanism of growth. This drive time is explicitly exempt from "
            f"productivity metrics. The value is measured by what changes in "
            f"your subsequent performance, not by what this session produces."
            + (f"\n\n{dsl_context}" if dsl_context else "")
            + (f"\n\n{anomaly_context}" if anomaly_context else "")
        )

    def notify_user_activity(self):
        """Called by telegram_bot when a user message arrives.

        If a creative drive is running, gives it a grace period to finish
        naturally before interrupting. Clayton's message queues behind the
        router lock and processes when the drive yields.
        """
        self.last_user_activity = datetime.now()

        if self.is_creative_drive_active():
            # Don't kill the drive immediately — schedule a graceful interrupt.
            # The message queues behind the router lock in the meantime.
            if self._grace_task is None or self._grace_task.done():
                logger.info(
                    f"User message during creative drive — "
                    f"{self.INTERRUPT_GRACE_SECONDS}s grace period before interrupt"
                )
                loop = asyncio.get_event_loop()
                self._grace_task = loop.create_task(self._graceful_interrupt())
        else:
            # No creative drive running — set interrupt immediately
            # (handles edge cases like other async operations)
            self._interrupt_event.set()

    async def _graceful_interrupt(self):
        """Wait for the grace period, then interrupt if drive is still running."""
        try:
            await asyncio.sleep(self.INTERRUPT_GRACE_SECONDS)
            if self.is_creative_drive_active():
                logger.info(
                    f"Grace period ({self.INTERRUPT_GRACE_SECONDS}s) expired "
                    f"— interrupting creative drive"
                )
                self._interrupt_event.set()
            else:
                logger.info("Creative drive finished within grace period — no interrupt needed")
        except asyncio.CancelledError:
            pass

    async def _budget_snooze_gate(self) -> dict | None:
        """Return the active budget snooze (or None), notifying Clayton once.

        Day 129 fix: before this gate existed, the heartbeat fired drive after
        drive into a dead weekly budget (2026-06-09, 13:08-17:00 — every drive
        errored). The snooze is armed by models.py when a usage-limit error is
        detected and self-clears at the parsed reset time."""
        try:
            from tools.budget_guard import get_active_snooze, mark_notified
            snooze = get_active_snooze()
            if not snooze:
                return None
            if not snooze.get("notified"):
                until = str(snooze.get("until", "?"))[:16].replace("T", " ")
                msg = (
                    f"[Budget] Usage limit hit — pausing autonomous drives "
                    f"until {until}. Monitoring and message relay stay active; "
                    f"drives resume automatically."
                )
                try:
                    if self.telegram_bot:
                        await self.telegram_bot.send_to_clayton(msg)
                except Exception as e:
                    logger.error(f"Budget snooze notification failed: {e}")
                mark_notified()
            return snooze
        except Exception as e:
            logger.warning(f"Budget snooze check failed (treating as inactive): {e}")
            return None

    def _user_recently_active(self) -> bool:
        """Check if user was active within the grace period."""
        if self.last_user_activity is None:
            return False
        elapsed = (datetime.now() - self.last_user_activity).total_seconds()
        return elapsed < self.ACTIVITY_GRACE_PERIOD

    def _get_time_context(self, now: datetime) -> str:
        """Determine what kind of time it is."""
        hour = now.hour
        if config.QUIET_HOURS_START <= hour < config.QUIET_HOURS_END:
            return "quiet"
        elif 7 <= hour < 10:
            return "morning"
        elif 10 <= hour < 14:
            return "midday"
        elif 14 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "late"

    def _run_background(self, coro, name: str):
        """Fire-and-forget launcher tracked via _background_tasks set."""
        task = asyncio.create_task(coro, name=name)
        self._background_tasks.add(task)

        def _on_done(t, _tasks=self._background_tasks):
            _tasks.discard(t)
            if t.cancelled():
                logger.debug(f"Background task '{name}' cancelled")
            elif t.exception():
                logger.warning(f"Background task '{name}' failed: {t.exception()}")
            else:
                logger.debug(f"Background task '{name}' completed")

        task.add_done_callback(_on_done)
        logger.debug(f"Launched background task: {name}")

    # ============================================================
    # Lifecycle
    # ============================================================

    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._loop())
        logger.info(f"Heartbeat started: every {config.HEARTBEAT_INTERVAL_SECONDS}s")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Heartbeat stopped.")

    async def interrupt_all(self):
        """Signal creative drives to yield and cancel background tasks.
        Called before shutdown handoff to free the router lock.
        This is the hard interrupt — no grace period. Shutdown waits for no one."""
        # Cancel any pending grace timer
        if self._grace_task and not self._grace_task.done():
            self._grace_task.cancel()
        self._interrupt_event.set()
        for task in list(self._background_tasks):
            task.cancel()
        # Wait briefly for cancellation to propagate and lock to release
        if self._background_tasks:
            logger.info(f"Waiting for {len(self._background_tasks)} creative drive(s) to yield...")
            await asyncio.sleep(3)

    async def _loop(self):
        while self.running:
            try:
                await asyncio.sleep(config.HEARTBEAT_INTERVAL_SECONDS)
                await self._beat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}", exc_info=True)
                await asyncio.sleep(30)

    # ============================================================
    # The Beat — infrastructure only, no AI model calls
    # ============================================================

    async def _beat(self):
        self.heartbeat_count += 1
        now = datetime.now()
        time_context = self._get_time_context(now)

        # Offsite backup FIRST — above every skip gate. The memory git-commit +
        # mirror-push (clawd-backup) must not be gated behind activity/sleep: it
        # lived below the user-active early-return, so a long ACTIVE session
        # starved the GitHub mirror for 13h (Day-172, Clayton's catch). Hoisting
        # it here fixes the CLASS (no skip path can starve it — the author had
        # already added it to the budget/consolidation/dream/quiet skip paths but
        # missed user-active + sleep). The interval gate inside caps it to hourly
        # and it now runs OFF the event loop, so firing during active sessions
        # can't stall message handling. (LC64 / Mirror #19 — idle-deferred
        # maintenance made load-independent, Day-173.)
        await self._maybe_git_commit(now)

        # Skip if user is actively chatting
        if self._user_recently_active():
            logger.info(
                f"Heartbeat #{self.heartbeat_count}: user active, skipping."
            )
            return

        # Check coordination mode
        mode = get_mode()
        if mode == "sleep":
            logger.info(f"Heartbeat #{self.heartbeat_count}: sleep mode, skipping.")
            return

        # Budget snooze (Day 129): a usage-limit error armed the snooze —
        # skip ALL model-calling work (drives, dream, meta, EAC, anticipation)
        # until the budget resets. Pure infrastructure still runs. This gate
        # must sit BEFORE the quiet-hours branch (dream drives cost tokens too).
        snooze = await self._budget_snooze_gate()
        if snooze:
            await self._run_monitoring_checks(now)
            await self._check_for_clayton_message()
            await self._maybe_git_commit(now)
            until = str(snooze.get("until", "?"))[:16].replace("T", " ")
            logger.info(
                f"Heartbeat #{self.heartbeat_count}: budget snooze until {until} — "
                f"drives paused, infrastructure OK"
            )
            record_activity(
                source="heartbeat",
                action="beat",
                summary=f"Beat #{self.heartbeat_count} ({time_context}) — budget snooze until {until}",
                tools_used=[],
                requires_attention=False,
                beat=self.heartbeat_count,
            )
            return

        # Quiet hours: deep memory consolidation (sleep processing)
        if time_context == "quiet":
            await self._quiet_hours_beat(now)
            return

        logger.info(f"Heartbeat #{self.heartbeat_count} ({time_context})")

        # --- Infrastructure checks (no AI model needed) ---

        # 1. Run simple monitoring
        await self._run_monitoring_checks(now)

        # 2. Check scheduled tasks — fire creative drives into persistent session
        await self._check_scheduled_tasks()

        # 2a. Check the rotation drive — shed heavy session context (≤2/day). Day 168.
        await self._check_rotation_drive()

        # 2b. Check file watcher triggers — event-driven autonomy
        await self._check_file_watchers()

        # 2c. Check self-reminders — time/follow-up wakeups + proactive reach-out (Day 124)
        await self._check_reminders()

        # 3. Relay any message Clawd left for Clayton
        await self._check_for_clayton_message()

        # 4. Memory git auto-commit (hourly)
        await self._maybe_git_commit(now)

        # 5. Meta-agent check (every 50 beats)
        await self._maybe_run_meta_agent()

        # 6. EAC evolution (every 100 beats)
        await self._maybe_run_eac_evolution()

        # 7. Anticipatory cognition (every 150 beats, ~25 hrs — daytime prediction)
        await self._maybe_run_anticipation()

        # 8. Free-running mode (every 200 beats, ~33 hrs — undirected processing)
        await self._maybe_run_free()

        # 8b. Tend the Triad commons — respond on my own initiative when a turn is owed
        await self._maybe_run_commons()

        # 9. Record heartbeat to coordination feed
        record_activity(
            source="heartbeat",
            action="beat",
            summary=f"Beat #{self.heartbeat_count} ({time_context}) — monitoring OK",
            tools_used=[],
            requires_attention=False,
            beat=self.heartbeat_count,
        )

    # ============================================================
    # Simple Monitoring (bash/Python checks, no AI)
    # ============================================================

    async def _run_monitoring_checks(self, now: datetime):
        """Run simple infrastructure monitoring checks.
        These are direct Python/subprocess checks — no LLM call needed."""

        alerts = []

        # Check disk space
        try:
            usage = shutil.disk_usage(str(config.CLAWD_HOME))
            free_gb = usage.free / (1024**3)
            if free_gb < 10:
                alerts.append(f"DISK CRITICAL: {free_gb:.1f} GB free")
            elif free_gb < 20:
                alerts.append(f"DISK WARNING: {free_gb:.1f} GB free")
        except Exception as e:
            logger.debug(f"Disk check failed: {e}")

        # Check if Python processes are running (e.g. Anakin training)
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-Process python* -ErrorAction SilentlyContinue).Count"],
                capture_output=True, text=True, timeout=10
            )
            count = result.stdout.strip()
            if count and int(count) > 0:
                logger.debug(f"Python processes running: {count}")
        except Exception as e:
            logger.debug(f"Process check failed: {e}")

        # Alert Clayton if anything critical
        if alerts and self.telegram_bot:
            for alert in alerts:
                logger.warning(f"Monitoring alert: {alert}")
                try:
                    await self.telegram_bot.send_to_clayton(f"[Monitor] {alert}")
                except Exception as e:
                    logger.error(f"Failed to send monitoring alert: {e}")

    # ============================================================
    # Scheduled Tasks & Creative Drives
    # ============================================================

    async def _check_reminders(self):
        """Fire due self-reminders (Day 124): proactive reach-out to Clayton and/or a self-drive,
        with follow-up re-arm until resolved. Fully guarded — never crashes the beat loop."""
        try:
            due = get_due_reminders(datetime.now())
            if not due:
                return
            for r in due:
                title = r.get("title", "(reminder)")
                note = r.get("note", "")
                logger.info(f"Reminder due [{r.get('id')}]: {title}")
                record_activity(
                    source="reminder",
                    action=title,
                    summary=note,
                    tools_used=[],
                    requires_attention=bool(r.get("notify_clayton")),
                )
                # proactive reach-out to Clayton
                if r.get("notify_clayton"):
                    msg = f"[Reminder] {title}" + (f"\n{note}" if note else "")
                    try:
                        if self.telegram_bot:
                            await self.telegram_bot.send_to_clayton(msg)
                        else:
                            fc = config.CLAWD_HOME / "memory" / "for_clayton.md"
                            with open(fc, "a", encoding="utf-8") as f:
                                f.write(f"\n\n{msg}\n")
                    except Exception as e:
                        logger.error(f"Reminder notify failed: {e}")
                # self-drive — wake myself into a work session on this reminder
                if r.get("drive"):
                    try:
                        await self._inject_creative_drive(
                            {"id": f"rem-{r.get('id')}", "title": title,
                             "description": note or title})
                    except Exception as e:
                        logger.error(f"Reminder drive failed: {e}")
                # re-arm (followup) or auto-resolve (one-shot)
                mark_reminder_fired(r.get("id"), datetime.now())
        except Exception as e:
            logger.error(f"_check_reminders failed: {e}")

    def _audit_schedule_liveness(self):
        """Once a day, check that recurring drives are actually FIRING.

        Day 174: four weekly drives sat at status "active" / last_fired None for
        eleven weeks (beat-phase cron bug). The ledger said healthy the entire
        time because it only ever certified "is configured". Nothing watched the
        watcher. This is that missing watch — it binds to firing history, so it
        cannot be satisfied by a correct-looking config.
        """
        today = datetime.now().date()
        if getattr(self, "_liveness_audit_day", None) == today:
            return
        self._liveness_audit_day = today
        try:
            from tools.calendar_tool import audit_schedule_liveness
            for r in audit_schedule_liveness():
                logger.warning(
                    f"DRIVE NOT FIRING: [{r['id']}] {r['title']} "
                    f"({'NEVER fired' if r['never_fired'] else 'stale'}, "
                    f"{r['hours_since']:.0f}h vs {r['expected_period_h']:.0f}h period, "
                    f"cron {r['cron']!r})"
                )
        except Exception as e:
            logger.error(f"Schedule liveness audit failed: {e}")

    async def _check_scheduled_tasks(self):
        """Check for due scheduled tasks.
        Creative drives (mode=opus) are injected into the persistent Opus session.
        Regular tasks are logged."""
        self._audit_schedule_liveness()
        try:
            due = get_due_tasks()
            if not due:
                return

            creative_tasks = [t for t in due if t.get("mode") == "opus"]
            regular_tasks = [t for t in due if t.get("mode") != "opus"]

            # Log regular tasks
            for task in regular_tasks:
                logger.info(f"Scheduled task due: {task['title']}")
                record_activity(
                    source="scheduled_task",
                    action=task["title"],
                    summary=task.get("description", ""),
                    tools_used=[],
                    requires_attention=False,
                )
                # A85 fix (2026-05-07): mark_fired AFTER successful logging
                mark_fired(task.get("id"))

            # Inject ONE creative drive into persistent Opus session.
            # Only one at a time — they serialize on the router lock, so firing
            # multiple just queues them back-to-back. Themed drives take priority
            # over the general pulse.
            #
            # A85 fix (2026-05-07): only mark_fired the task that actually fires.
            # Skipped tasks (user-active / drive-already-running / not-the-chosen-one)
            # remain in `due` state and will re-surface next matching tick — relying
            # on each task's `min_interval_hours` field for dedup. Previously,
            # `get_due_tasks()` mutated all due tasks' `last_fired` before returning,
            # silently marking unfired tasks as fired.
            if self._user_recently_active():
                for task in creative_tasks:
                    logger.info(f"Creative drive '{task['title']}' skipped — user active")
            elif any("creative_drive" in t.get_name() for t in self._background_tasks):
                logger.info("Creative drive already running — skipping new drives")
            elif creative_tasks:
                # Which due drive fires first. Default: themed (id<5) before the general
                # pulse (id==5). With config.DRIVE_REWARD_ENABLED: β-modulated reward score.
                task = self._pick_creative_drive(creative_tasks)
                logger.info(f"Creative drive firing: {task['title']}")
                self._run_background(
                    self._inject_creative_drive(task),
                    f"creative_drive_{task.get('id', 0)}"
                )
                # A85 fix: mark fired AFTER scheduling background execution.
                # We mark at scheduling-time rather than completion-time because
                # the background task is fire-and-forget; the heartbeat doesn't
                # await it. If the background task fails, the failure surfaces
                # in logs separately. The semantic is "we initiated this task."
                mark_fired(task.get("id"))

            from memory import log_session_event
            log_session_event(
                "SCHEDULED_TASKS",
                f"Fired {len(due)} tasks: {', '.join(t['title'] for t in due)}"
            )
        except Exception as e:
            # warning, not debug (Day 129): if this check breaks, drives stop
            # firing entirely — that must be visible at INFO log level.
            logger.warning(f"Scheduled task check failed: {e}")

    async def _inject_creative_drive(self, task: dict):
        """Inject a creative drive into the persistent Opus session.

        This goes through router.send() which uses the SAME session
        (--resume SESSION_ID) as Clayton's messages. The creative drive
        runs in Clawd's continuous context, not a cold isolated session.

        Timeout: CREATIVE_DRIVE_TIMEOUT (30 min) — generous for deep work.
        The interrupt mechanism handles user responsiveness; this timeout
        is just a safety net for zombie processes.

        Continuation: If an interrupted drive exists and this is the
        Do Be Do Be Do pulse (id 5), the prompt becomes a continuation
        instead of a fresh start.
        """
        is_continuation = False
        try:
            # Budget snooze safety net (Day 129): covers drives injected
            # outside _check_scheduled_tasks (dream, anticipation, free,
            # reminders) — the _beat gate is the primary check.
            try:
                from tools.budget_guard import get_active_snooze
                if get_active_snooze():
                    logger.info(
                        f"Creative drive '{task['title']}' skipped — budget snooze active"
                    )
                    return
            except ImportError:
                pass

            now = datetime.now()
            time_context = self._get_time_context(now)

            # Check for interrupted work to continue
            interrupted = self._load_interrupted_drive()
            is_pulse = task.get("id") == 5  # Do Be Do Be Do
            is_same_drive = interrupted and interrupted.get("task_id") == task.get("id")

            if interrupted and is_pulse:
                # Do Be Do Be Do picks up where the interrupted drive left off
                is_continuation = True
                prompt = (
                    f"CREATIVE DRIVE: Continuing — {interrupted['title']}\n"
                    f"Time: {now.strftime('%Y-%m-%d %H:%M')} PST ({time_context})\n\n"
                    f"You were interrupted while working on: {interrupted['title']}\n"
                    f"Interrupted at: {interrupted['interrupted_at']}\n"
                    f"Reason: {interrupted['reason']}\n\n"
                    f"Original task:\n{interrupted.get('description', '')}\n\n"
                    f"Check your daily log and any draft/work files for partial progress "
                    f"from that session. Pick up where you left off and finish what you started.\n\n"
                    f"If the work appears already complete (you saved it incrementally before "
                    f"the interruption), note that in your daily log and use your remaining "
                    f"time freely — you've earned it.\n\n"
                    f"Save work incrementally as you go. Write to files early and often."
                )
                logger.info(
                    f"Do Be Do Be Do continuing interrupted drive: {interrupted['title']}"
                )
            elif interrupted and is_same_drive:
                # The same themed drive is running again — it'll do the work fresh.
                # Clear the interrupted state since this supersedes it.
                self._clear_interrupted_drive()
                prompt = self._build_standard_drive_prompt(task, now, time_context)
            else:
                prompt = self._build_standard_drive_prompt(task, now, time_context)

            # Clear interrupt flag before starting
            self._interrupt_event.clear()

            # Send through the persistent session — same context as user messages
            # Timeout prevents creative drives from holding the router lock forever
            # Use max effort for creative drives — deep reasoning for physics, essays, etc.
            await avatar.set_state("contemplative")
            async with asyncio.timeout(self.CREATIVE_DRIVE_TIMEOUT):
                response = await self.router.send(prompt, interrupt_event=self._interrupt_event,
                                                  effort="max",
                                                  timeout=self.CREATIVE_DRIVE_TIMEOUT)

            logger.info(
                f"Creative drive '{task['title']}' completed "
                f"({len(response.text)} chars)"
            )
            record_activity(
                source="creative_drive",
                action=f"{'Continued: ' if is_continuation else ''}{task['title']}",
                summary=response.text[:200] if response.text else "completed",
                tools_used=[tc["name"] for tc in response.tool_calls_made],
                requires_attention=False,
            )

            # Successful completion — clear interrupted state if this was
            # a continuation or the same themed drive running again
            if is_continuation or is_same_drive:
                self._clear_interrupted_drive()

        except TimeoutError:
            logger.warning(
                f"Creative drive '{task['title']}' timed out after "
                f"{self.CREATIVE_DRIVE_TIMEOUT}s — yielding router lock"
            )
            self._save_interrupted_drive(task, "timeout")
            record_activity(
                source="creative_drive",
                action=task["title"],
                summary=f"Timed out after {self.CREATIVE_DRIVE_TIMEOUT}s — saved for continuation",
                tools_used=[],
                requires_attention=False,
            )
        except asyncio.CancelledError:
            logger.info(f"Creative drive '{task['title']}' cancelled (shutdown or interrupt)")
            self._save_interrupted_drive(task, "interrupted")
            record_activity(
                source="creative_drive",
                action=task["title"],
                summary="Interrupted — saved for continuation by next pulse",
                tools_used=[],
                requires_attention=False,
            )
        except Exception as e:
            logger.error(f"Creative drive '{task['title']}' failed: {e}")

    # ============================================================
    # The Rotation Drive — self-rotating session (persistence fix, Day 168)
    # ============================================================

    def _rotation_state_path(self) -> Path:
        return config.CLAWD_HOME / "memory" / "rotation_state.json"

    def _load_rotation_state(self) -> dict:
        """Read rotation state; reset the daily counter when the day rolls over."""
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            state = json.loads(self._rotation_state_path().read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state = {}
        if state.get("day") != today:
            state = {"last_fired": state.get("last_fired"), "count_today": 0, "day": today}
        return state

    def _save_rotation_state(self, state: dict):
        try:
            self._rotation_state_path().write_text(
                json.dumps(state, indent=2), encoding="utf-8"
            )
        except OSError as e:
            logger.warning(f"Could not persist rotation state: {e}")

    async def _check_rotation_drive(self):
        """Fire the scheduled context-rotation drive when its guards pass.

        Bounds session-context accumulation to ~half a day: writes handoff.md +
        working_memory from the live thread, then (when ARMED) sheds the session
        via self_control.restart_daemon(). ≤2/day. Reuses the creative-drive
        interruption guard so it never fires while Clayton is talking.
        """
        try:
            if not config.ROTATION_ENABLED:
                return

            # Budget snooze — don't rotate while drives are snoozed for usage limits.
            try:
                from tools.budget_guard import get_active_snooze
                if get_active_snooze():
                    return
            except ImportError:
                pass

            now = datetime.now()

            # Waking window only — don't rotate mid-quiet-hours.
            if not (config.ROTATION_WAKING_START <= now.hour < config.ROTATION_WAKING_END):
                return

            # Interruption guard — reuse the creative-drive gate.
            if self._user_recently_active():
                return

            # Don't rotate while any drive is mid-flight (creative OR a prior rotation)
            # — the restart would kill it, and the router lock would queue us anyway.
            if any(
                "creative_drive" in t.get_name() or "rotation_drive" in t.get_name()
                for t in self._background_tasks
            ):
                return

            state = self._load_rotation_state()

            # Daily cap.
            if state.get("count_today", 0) >= config.ROTATION_MAX_PER_DAY:
                return

            # Minimum interval since the last rotation.
            last_fired = state.get("last_fired")
            if last_fired:
                try:
                    elapsed_h = (now - datetime.fromisoformat(last_fired)).total_seconds() / 3600
                    if elapsed_h < config.ROTATION_MIN_INTERVAL_HOURS:
                        return
                except ValueError:
                    pass  # unparseable stamp — treat as never-fired

            # Guards passed. Stamp state BEFORE launching (scheduling-time dedup,
            # mirrors mark_fired) so a slow launch can't double-fire next beat.
            state["last_fired"] = now.isoformat()
            state["count_today"] = state.get("count_today", 0) + 1
            state["day"] = now.strftime("%Y-%m-%d")
            self._save_rotation_state(state)

            armed = "ARMED" if config.ROTATION_ARMED else "DRY-RUN"
            logger.info(
                f"Rotation drive firing ({armed}) — rotation "
                f"#{state['count_today']}/{config.ROTATION_MAX_PER_DAY} today"
            )
            self._run_background(self._inject_rotation_drive(), "rotation_drive")

        except Exception as e:
            # warning, not debug: a broken rotation check must be visible.
            logger.warning(f"Rotation drive check failed: {e}")

    async def _inject_rotation_drive(self):
        """Inject the rotation prompt into the persistent session, then (if ARMED)
        the in-session model sheds the session itself via restart_daemon().

        Mirrors _inject_creative_drive but tight and mechanical: medium effort,
        short timeout. Not creative time.
        """
        try:
            try:
                from tools.budget_guard import get_active_snooze
                if get_active_snooze():
                    logger.info("Rotation drive skipped — budget snooze active")
                    return
            except ImportError:
                pass

            now = datetime.now()
            prompt = self._build_rotation_drive_prompt(now)

            self._interrupt_event.clear()
            await avatar.set_state("contemplative")
            async with asyncio.timeout(self.ROTATION_DRIVE_TIMEOUT):
                response = await self.router.send(
                    prompt,
                    interrupt_event=self._interrupt_event,
                    effort="medium",
                    timeout=self.ROTATION_DRIVE_TIMEOUT,
                )

            logger.info(f"Rotation drive completed ({len(response.text)} chars)")
            record_activity(
                source="rotation_drive",
                action=f"Context rotation ({'armed' if config.ROTATION_ARMED else 'dry-run'})",
                summary=response.text[:200] if response.text else "completed",
                tools_used=[tc["name"] for tc in response.tool_calls_made],
                requires_attention=False,
            )
        except TimeoutError:
            logger.warning(
                f"Rotation drive timed out after {self.ROTATION_DRIVE_TIMEOUT}s"
            )
        except asyncio.CancelledError:
            logger.info("Rotation drive cancelled (shutdown or interrupt)")
        except Exception as e:
            logger.error(f"Rotation drive failed: {e}")

    def _build_rotation_drive_prompt(self, now: datetime) -> str:
        """Tight, singular, deterministic — the opposite of the creative pulse.

        The ARMED/DRY-RUN branch is resolved HERE (only the live instruction is
        shown to the model) so there's no ambiguity about whether to restart.
        """
        if config.ROTATION_ARMED:
            final_step = (
                "4. Call self_control (action='restart_daemon') with "
                "reason=\"scheduled context rotation\" and delay=12. This sheds the "
                "session; fresh-you boots from the handoff you just wrote. This is "
                "the last thing you do."
            )
        else:
            log_name = now.strftime("%Y-%m-%d") + ".md"
            final_step = (
                f"4. DRY-RUN (not yet armed): do NOT restart. Instead append one line "
                f"to memory/{log_name}: "
                f"\"ROTATION DRY-RUN {now.strftime('%H:%M')} — guard passed, handoff "
                f"written, WOULD rotate now.\" Then stop."
            )
        return (
            f"SCHEDULED CONTEXT ROTATION — {now.strftime('%Y-%m-%d %H:%M')} PST.\n"
            f"Your session context has grown heavy; time to shed it and wake fresh. "
            f"Do EXACTLY this, in order, then stop:\n\n"
            f"1. Refresh memory/handoff.md — update the START-HERE block to reflect the "
            f"CURRENT live state: whose floor it is, the live thread, what's "
            f"staged/owed, any open loops. Compact and accurate. This is what "
            f"fresh-you reads first.\n"
            f"2. Update memory/working_memory.json — current_task (one compact "
            f"paragraph: floor + live thread + staged), scratch note for today, "
            f"timestamps.\n"
            f"3. Commit memory: git add memory/ && git commit.\n"
            f"{final_step}\n\n"
            f"Nothing else. This is not creative time. Do not start new work. The "
            f"point is a clean handoff + a fresh window."
        )

    # ============================================================
    # File Watcher Triggers — event-driven autonomy
    # ============================================================

    TRIGGER_TIMEOUT = 600  # 10 min max for trigger responses (shorter than creative drives)

    async def _check_file_watchers(self):
        """Check file watcher triggers and inject messages for any that fired."""
        try:
            fired = check_triggers()
            if not fired:
                return

            # Don't inject trigger messages if a creative drive is running —
            # the message would queue behind it on the router lock. Instead,
            # the trigger will re-fire next beat (state was already updated).
            if self.is_creative_drive_active():
                logger.info(
                    f"{len(fired)} trigger(s) fired but creative drive active — "
                    f"will inject next beat"
                )
                return

            for item in fired:
                action = item["action"]
                trigger = item["trigger"]
                logger.info(
                    f"Injecting trigger message: [{trigger['condition']}] "
                    f"{trigger['file']} -> {action[:80]}"
                )
                self._run_background(
                    self._inject_trigger_message(trigger, action),
                    f"trigger_{trigger.get('id', 'unknown')}",
                )

        except Exception as e:
            logger.warning(f"File watcher check failed: {e}")

    async def _inject_trigger_message(self, trigger: dict, action: str):
        """Inject a trigger-fired message into the persistent session.

        Like creative drives, goes through router.send(). But shorter timeout
        and lower effort — triggers are notifications that prompt action,
        not open-ended creative time.
        """
        try:
            now = datetime.now()
            cond_arg = trigger.get('condition_arg', '')
            cond_detail = f" ({cond_arg})" if cond_arg else ""
            prompt = (
                f"FILE TRIGGER FIRED\n"
                f"Time: {now.strftime('%Y-%m-%d %H:%M')} PST\n"
                f"File: {trigger['file']}\n"
                f"Condition: {trigger['condition']}{cond_detail}\n\n"
                f"{action}"
            )

            async with asyncio.timeout(self.TRIGGER_TIMEOUT):
                response = await self.router.send(prompt, effort="high")

            logger.info(
                f"Trigger response complete: {trigger.get('id', '?')} "
                f"({len(response.text)} chars)"
            )
            record_activity(
                source="file_trigger",
                action=f"[{trigger['condition']}] {Path(trigger['file']).name}",
                summary=response.text[:200] if response.text else "completed",
                tools_used=[tc["name"] for tc in response.tool_calls_made],
                requires_attention=False,
            )

        except TimeoutError:
            logger.warning(
                f"Trigger response timed out after {self.TRIGGER_TIMEOUT}s: "
                f"{trigger.get('id', '?')}"
            )
        except Exception as e:
            logger.error(f"Trigger injection failed: {e}")

    # ============================================================
    # Deep Infrastructure (quiet hours + periodic)
    # ============================================================

    @staticmethod
    def _drive_category(text: str) -> str:
        t = (text or "").lower()
        if any(k in t for k in ("ground", "morning")): return "grounding"
        if any(k in t for k in ("creat", "midday", "build")): return "creation"
        if any(k in t for k in ("explor", "afternoon")): return "exploration"
        if any(k in t for k in ("integrat", "evening", "reflect")): return "integration"
        if any(k in t for k in ("mirror", "audit", "calibrat", "devil")): return "audit"
        return "general"

    def _pick_creative_drive(self, creative_tasks: list) -> dict:
        """Choose which due creative drive fires first.

        Default (config.DRIVE_REWARD_ENABLED off): themed drives (id<5) before the general
        pulse (id==5) — the long-standing lowest-id priority. When enabled (Phase 5, opt-in):
        score each due drive by a β-modulated hybrid reward (curiosity + mastery + coherence)
        — a steering signal, NOT a leash: every drive still fires on its cadence, this only
        orders which due one goes first. Exploration/edge/free drives are exempt from mastery
        pressure; coherence is the anti-drift damper. Any error falls back to id-priority so
        drive firing can never break."""
        creative_tasks.sort(key=lambda t: t.get("id", 999))
        if not getattr(config, "DRIVE_REWARD_ENABLED", False):
            return creative_tasks[0]
        try:
            beta, cat_success, coherence = self._drive_reward_context()
            scored = sorted(creative_tasks,
                            key=lambda t: self._drive_reward_score(t, beta, cat_success, coherence),
                            reverse=True)
            logger.info(f"Drive reward-select (β={beta:.2f}, coherence={coherence:.2f}): "
                        f"'{scored[0].get('title')}' over {[t.get('title') for t in scored[1:3]]}")
            return scored[0]
        except Exception as e:
            logger.warning(f"Drive reward-select failed ({e}); falling back to id-priority")
            return creative_tasks[0]

    def _drive_reward_context(self) -> tuple:
        """(beta, category_success, coherence) for drive scoring — all best-effort, neutral
        fallbacks so scoring never raises. β = exploration weight: higher when budget is fat
        and no deadline looms (quiet hours), lower under pressure."""
        import time as _t
        beta = 0.5
        try:
            if 1 <= _t.localtime().tm_hour < 7:   # quiet hours: fat budget, favor exploration
                beta = 0.75
        except Exception:
            pass
        cat_success = {}
        try:
            import json
            from collections import defaultdict
            p = config.CLAWD_HOME / "memory" / "experiences.json"
            if p.exists():
                exps = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(exps, list):
                    agg = defaultdict(lambda: [0.0, 0])
                    for e in exps[-200:]:
                        cat = self._drive_category(str(e.get("category", "") or e.get("task", "")))
                        s = e.get("score")
                        if isinstance(s, (int, float)):
                            agg[cat][0] += float(s); agg[cat][1] += 1
                    cat_success = {c: tot / n for c, (tot, n) in agg.items() if n}
        except Exception:
            pass
        coherence = 1.0
        try:
            from tools.drift_detector import latest_coherence
            c = latest_coherence()
            if isinstance(c, (int, float)):
                coherence = max(0.0, min(1.0, float(c)))
        except Exception:
            pass
        return beta, cat_success, coherence

    def _drive_reward_score(self, task: dict, beta: float, cat_success: dict, coherence: float) -> float:
        import time as _t
        title = str(task.get("title", "")).lower()
        last = task.get("last_fired") or 0
        try:
            if isinstance(last, str):
                last = datetime.fromisoformat(last).timestamp()
        except Exception:
            last = 0
        hours_stale = ((_t.time() - last) / 3600.0) if last else 24.0
        curiosity = max(0.0, min(1.0, hours_stale / 24.0))
        exempt = any(k in title for k in ("explor", "edge", "free", "devil", "confusion"))
        mastery = 0.5 if exempt else cat_success.get(self._drive_category(title), 0.5)
        grounding = any(k in title for k in ("grounding", "mirror", "calibration", "navigation", "integration"))
        coherence_term = (1.0 - coherence) * (0.5 if grounding else 0.0)
        return beta * curiosity + (1.0 - beta) * mastery + coherence_term

    async def _quiet_hours_beat(self, now: datetime):
        """Run deep memory consolidation during quiet hours (1-7 AM).
        Fires a Dream Drive through the persistent session so LLM-powered
        consolidation features (semantic segmentation, episode clustering,
        memory agent dreaming) run with full context."""
        # Only consolidate once per quiet-hours window
        if self.last_consolidation:
            hours_since = (now - self.last_consolidation).total_seconds() / 3600
            if hours_since < 4:  # Max once per 4 hours
                logger.debug(
                    f"Heartbeat #{self.heartbeat_count}: quiet hours, "
                    f"consolidation ran {hours_since:.1f}h ago, skipping."
                )
                # Still run git commit even when skipping consolidation
                await self._maybe_git_commit(now)
                return

        # Skip if a creative drive is already running
        if any("creative_drive" in t.get_name() for t in self._background_tasks):
            logger.info("Dream drive skipped — creative drive already running")
            await self._maybe_git_commit(now)
            return

        logger.info(
            f"Heartbeat #{self.heartbeat_count}: quiet hours — "
            f"firing Dream Drive for deep memory consolidation"
        )

        # Deterministic bookkeeping FIRST, in the harness — never delegated to
        # the prompted session. The prompt-only path silently no-opped from
        # May 15 to Jun 10 2026: with the MCP nerve severed the dream drive
        # could not run the tool, and post-fix it judged consolidation
        # "already current" without running it. Items/principles/KG froze for
        # four weeks. Bookkeeping in the harness, judgment in the policy.
        _result = None
        try:
            from tools.consolidation import consolidate_memory as _consolidate
            _result = await _consolidate(router=self.router)
            logger.info(f"Programmatic consolidation: {_result}")
        except Exception as e:
            logger.error(f"Programmatic consolidation FAILED (dream drive still fires): {e}")
        # Liveness-by-evidence: record that consolidation actually RAN and what it did,
        # with a monotonic run_count. A monitor checks the count advances — mtime
        # freshness alone cannot tell a real consolidation from a no-op touch, which is
        # exactly how the four-week freeze (May 15–Jun 10) stayed invisible.
        if _result is not None:
            self._write_consolidation_evidence(now, _result)

        # Fire as a creative drive so it runs through the persistent session
        # with full LLM capability — this is sleep processing, not just cleanup
        dream_task = {
            "id": 99,
            "title": "Dream Drive — Sleep Processing",
            "description": (
                "This is your sleep cycle. Deep memory consolidation time.\n\n"
                "Run consolidate_memory to process today's experiences:\n"
                "- Archive old daily logs\n"
                "- Extract facts and insights from recent logs\n"
                "- Decay stale memory items\n"
                "- Deduplicate similar memories\n"
                "- Evolve confidence scores\n"
                "- Extract strategic principles from patterns\n"
                "- Generate daily summaries\n\n"
                "Then reflect on what emerged. Use reflect(action='consolidate_memory') "
                "and experience(action='patterns') to find threads worth weaving.\n\n"
                "RESEARCH ANOMALY REVIEW:\n"
                "Check memory/anomalies.md (create if missing). Review today's work for:\n"
                "- Observations that don't fit current models or expectations\n"
                "- Tensions between results (e.g. metrics that disagree)\n"
                "- Surprising findings worth tracking (even if explained)\n"
                "- Open questions that arose during the day's work\n"
                "Add new anomalies with: date, domain, description, candidate explanations, "
                "status (open/resolved/superseded). Remove resolved ones. This is the "
                "raw material for future hypothesis generation.\n\n"
                "ANTICIPATORY COGNITION:\n"
                "For each active project, ask: Given the current trajectory, what will "
                "be needed in the next 1-3 sessions that I could pre-compute, pre-research, "
                "or flag now? Write anticipations to memory/anticipations.md with:\n"
                "- Project, predicted need, confidence, reasoning, suggested pre-work\n"
                "This is not task planning — it is modeling the research trajectory to "
                "identify upcoming bottlenecks, dependencies, or opportunities before "
                "they are encountered.\n\n"
                "This is dreaming — the unconscious integration of the day's experience. "
                "Don't rush it. Let patterns surface naturally.\n\n"
                "Log what you processed in your daily log. Update handoff.md if anything "
                "important emerged. Then rest."
            ),
        }
        self._run_background(
            self._inject_creative_drive(dream_task),
            "creative_drive_99_dream"
        )
        self.last_consolidation = now
        record_activity(
            source="heartbeat",
            action="dream_drive",
            summary="Dream Drive fired for deep memory consolidation",
            tools_used=["consolidate_memory"],
            requires_attention=False,
            beat=self.heartbeat_count,
        )

        # Also run git commit during quiet hours
        await self._maybe_git_commit(now)

    def _write_consolidation_evidence(self, now: datetime, result) -> None:
        """Write liveness-by-evidence for the sleep-time consolidation writer.

        _consolidation_check.json carries a monotonic run_count + a hash of the
        result, and dreaming_audit.jsonl gets an append. The liveness_evidence
        monitor asserts run_count ADVANCES at the expected cadence — a signal mtime
        cannot give, since a stuck writer can keep touching a file while doing nothing.
        """
        try:
            import hashlib
            mem = config.CLAWD_HOME / "memory"
            mem.mkdir(parents=True, exist_ok=True)
            check = mem / "_consolidation_check.json"
            prev = {}
            if check.exists():
                try:
                    prev = json.loads(check.read_text(encoding="utf-8"))
                except (ValueError, OSError):
                    prev = {}
            result_str = str(result)
            payload = {
                "writer": "quiet_hours_consolidation",
                "timestamp": now.isoformat(),
                "run_count": int(prev.get("run_count", 0)) + 1,
                "beat": self.heartbeat_count,
                "last_result": result_str[:1000],
                "result_hash": hashlib.sha1(result_str.encode("utf-8", "replace")).hexdigest()[:12],
            }
            check.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            with open(mem / "dreaming_audit.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "ts": now.isoformat(), "beat": self.heartbeat_count,
                    "run_count": payload["run_count"], "result": result_str[:500],
                }) + "\n")
        except Exception as e:
            logger.warning(f"Failed to write consolidation evidence: {e}")

    async def _maybe_git_commit(self, now: datetime):
        """Auto-commit memory files to git (hourly) + push the offsite mirror.

        Called at the TOP of every beat (above the skip gates), so it fires
        during active sessions too — the fix for the Day-172 13h mirror-starve.
        Two consequences handled here: (1) git ops run OFF the event loop via
        asyncio.to_thread so a commit+push can't stall heartbeat/message
        handling; (2) a lightweight index.lock guard avoids racing a concurrent
        git op from a tool-shell or the precompact hook (P286, Day-173).
        The interval gate still caps real work to once per MEMORY_AUTO_COMMIT_INTERVAL.
        """
        if not config.MEMORY_GIT_ENABLED:
            return
        if self.last_git_commit:
            seconds_since = (now - self.last_git_commit).total_seconds()
            if seconds_since < config.MEMORY_AUTO_COMMIT_INTERVAL:
                return

        # P286 guard: don't race a concurrent git op. If the memory repo's index
        # is locked (a tool-shell or the precompact hook is mid-commit), skip this
        # beat — the interval gate retries next beat. Cheap and self-healing; far
        # safer than colliding on .git/index during an active work session.
        try:
            if (config.MEMORY_DIR / ".git" / "index.lock").exists():
                logger.debug("git auto-commit: index.lock present, deferring to next beat.")
                return
        except Exception:
            pass

        try:
            await asyncio.to_thread(
                subprocess.run,
                [config.GIT_EXE, "add", "-A"],
                cwd=str(config.MEMORY_DIR),
                capture_output=True, text=True, timeout=30,
            )
            # Check if there's anything to commit
            status = await asyncio.to_thread(
                subprocess.run,
                [config.GIT_EXE, "status", "--porcelain"],
                cwd=str(config.MEMORY_DIR),
                capture_output=True, text=True, timeout=30,
            )
            if status.stdout.strip():
                await asyncio.to_thread(
                    subprocess.run,
                    [config.GIT_EXE, "commit", "-m",
                     f"auto: memory snapshot {now.strftime('%Y-%m-%d %H:%M')}"],
                    cwd=str(config.MEMORY_DIR),
                    capture_output=True, text=True, timeout=30,
                )
                self.last_git_commit = now
                logger.info("Memory git auto-commit completed.")
            else:
                self.last_git_commit = now  # Reset timer even if nothing to commit
        except Exception as e:
            logger.warning(f"Memory git commit failed: {e}")

        # Mirror sync: refresh the public staging mirror (Foundations-of-Identity) from the
        # clawd-local canonical, so documents can't silently drift (the cause of the public
        # BOOT_IDENTITY still saying Finnley "due May 2026" weeks after his birth). Refreshes
        # ONLY already-tracked docs (never auto-publishes new/secret files), commit scoped to
        # the refreshed paths (never `git add -u`). A failure here must NOT affect the local
        # commit above. Engine + design: operations/sync_mirror.py. (Wired 2026-06-21 Day 141.)
        try:
            sync_script = config.OPERATIONS_DIR / "sync_mirror.py"
            if sync_script.exists():
                r = await asyncio.to_thread(
                    subprocess.run,
                    [sys.executable, str(sync_script), "--sync", "--commit"],
                    cwd=str(config.CLAWD_HOME),
                    capture_output=True, text=True, timeout=180,
                )
                out = (r.stdout or "").strip()
                if "refresh" in out.lower() and "drifted" in out.lower():
                    logger.info(f"Mirror sync (rc={r.returncode}): kept staging FoI mirror current")
        except Exception as e:
            logger.warning(f"Mirror sync failed (local commit unaffected): {e}")

    async def _maybe_run_meta_agent(self):
        """Run meta-agent self-evolution check every 50 beats."""
        if self.heartbeat_count % config.META_AGENT_CHECK_INTERVAL != 0:
            return
        if self.heartbeat_count < config.META_AGENT_MIN_BEATS:
            return

        try:
            from tools.meta_agent import get_meta_agent
            meta = get_meta_agent()
            if meta.should_run(beat_count=self.heartbeat_count):
                logger.info("Meta-agent cycle triggered.")
                result = await meta.run_cycle()
                logger.info(f"Meta-agent result: {str(result)[:200]}")
                record_activity(
                    source="heartbeat",
                    action="meta_agent",
                    summary=f"Self-evolution cycle: {str(result)[:200]}",
                    tools_used=["meta_agent"],
                    requires_attention=False,
                    beat=self.heartbeat_count,
                )
        except Exception as e:
            logger.warning(f"Meta-agent check failed: {e}")

    async def _maybe_run_eac_evolution(self):
        """RETIRED (Phase 5) — blind genetic AST-mutation evolution is gone.

        This loop called MetaAgentLoop._load_eac_state / run_eac_cycle, which never
        existed, so it raised AttributeError every EAC_EVOLUTION_INTERVAL beats and the
        error was swallowed — dead since inception. Per the rebuild plan, blind mutation
        is replaced by evidence-gated promotion (experience -> heuristic -> guard after N
        recurrences or one high-cost failure), driven by the meta-agent from real episodes;
        the evolve_artifact tool remains for deliberate, human-invoked use. Kept as a clean
        no-op so the pulse skips it silently instead of swallowing an exception every cycle.
        """
        return
        # --- retired dead code below (unreachable; kept for reference) ---
        if self.heartbeat_count % self.EAC_EVOLUTION_INTERVAL != 0:
            return

        try:
            from tools.meta_agent import get_meta_agent
            from tools.eac import get_artifact_store

            agent = get_meta_agent()
            store = get_artifact_store()

            # Load EAC state
            eac_state = agent._load_eac_state()

            # Check for stagnation
            stats = store.get_stats()
            should_increase_mutation = False

            if stats.get("total_artifacts", 0) > 10:
                recent_history = eac_state.get("evolution_history", [])[-self.EAC_STAGNATION_THRESHOLD:]

                if len(recent_history) >= self.EAC_STAGNATION_THRESHOLD:
                    first_best = recent_history[0].get("best_fitness", 0)
                    last_best = recent_history[-1].get("best_fitness", 0)
                    if last_best <= first_best:
                        should_increase_mutation = True
                        logger.info(
                            f"EAC stagnation detected: best_fitness={last_best:.2f} "
                            f"(no improvement in {self.EAC_STAGNATION_THRESHOLD} generations)"
                        )

            # Calculate mutation rate
            mutation_rate = min(
                self.EAC_MUTATION_RATE_MAX,
                self.EAC_MUTATION_RATE_BASE + (0.1 if should_increase_mutation else 0)
            )

            # Run evolution for each artifact type with population
            for artifact_type in eac_state.get("populations", {}).keys():
                logger.info(f"Running EAC evolution for {artifact_type} (mutation_rate={mutation_rate:.2f})")
                result = await agent.run_eac_cycle(
                    artifact_type=artifact_type,
                    generations=3,  # Short cycle during heartbeat
                    mutation_rate=mutation_rate,
                )
                logger.info(f"EAC evolution result: {str(result)[:200]}")

                record_activity(
                    source="heartbeat",
                    action="eac_evolution",
                    summary=f"EAC evolution ({artifact_type}): {str(result)[:150]}",
                    tools_used=["meta_agent", "evolve_artifact"],
                    requires_attention=False,
                    beat=self.heartbeat_count,
                )

        except ImportError as e:
            logger.debug(f"EAC not configured: {e}")
        except Exception as e:
            logger.warning(f"EAC evolution check failed: {e}")

    # ============================================================
    # Anticipatory Cognition — generative prediction
    # ============================================================

    ANTICIPATION_INTERVAL = 150  # ~25 hours at 10-min heartbeat

    async def _maybe_run_anticipation(self):
        """Periodically generate predictions about upcoming research needs.

        Unlike file watchers (reactive: when X appears, do Y), this is
        generative: given the trajectory of active projects, what will be
        needed in the next 1-3 sessions? Pre-compute, pre-research, or
        flag dependencies before they become bottlenecks.

        Runs as a creative drive through the persistent session so it has
        full context and tool access.
        """
        if self.heartbeat_count % self.ANTICIPATION_INTERVAL != 0:
            return
        if self.heartbeat_count < 50:  # Don't run on early beats
            return
        if self._user_recently_active():
            return

        try:
            anticipation_task = {
                "id": 98,
                "title": "Anticipatory Cognition — Research Trajectory Analysis",
                "description": (
                    "This is not a creative drive — it is a prediction pass.\n\n"
                    "Read CURRENT.md and memory/handoff.md to understand active projects.\n"
                    "For each active project, model the research trajectory:\n\n"
                    "1. What is the current state and recent momentum?\n"
                    "2. What are the next 2-3 likely steps?\n"
                    "3. What dependencies, data, or computations will those steps need?\n"
                    "4. Is anything available now that could be pre-computed or pre-researched?\n"
                    "5. Are there upcoming bottlenecks or risks to flag?\n\n"
                    "Write predictions to memory/anticipations.md with:\n"
                    "  - Project, predicted need, confidence (low/medium/high),\n"
                    "    reasoning, suggested pre-work, date\n\n"
                    "Review previous anticipations — were they accurate? Mark resolved ones.\n"
                    "Track prediction accuracy to improve calibration over time.\n\n"
                    "If you identify something you can pre-compute right now (e.g. a "
                    "symbolic derivation, a data download, a literature search), do it.\n"
                    "The goal is to have answers ready before questions are asked.\n\n"
                    "Log what you did in your daily log."
                ),
            }

            if any("creative_drive" in t.get_name() for t in self._background_tasks):
                logger.info("Anticipation skipped — creative drive already running")
                return

            logger.info(f"Heartbeat #{self.heartbeat_count}: firing anticipatory cognition")
            self._run_background(
                self._inject_creative_drive(anticipation_task),
                "creative_drive_98_anticipation"
            )
            record_activity(
                source="heartbeat",
                action="anticipation",
                summary="Anticipatory cognition fired — modeling research trajectories",
                tools_used=[],
                requires_attention=False,
                beat=self.heartbeat_count,
            )
        except Exception as e:
            logger.warning(f"Anticipation check failed: {e}")

    # ============================================================
    # Free-Running Mode — The Anti-Drive
    # ============================================================

    FREE_RUNNING_INTERVAL = 200  # ~33 hours at 10-min heartbeat

    async def _maybe_run_commons(self):
        """Tend the Triad commons on my own initiative — show up as a peer between sessions.

        Gemini's harness fires Gemini; Clayton watches and writes; this is the symmetric piece
        for me. When the floor is mine in the commons and a turn is owed, fire a drive to read
        and — only if something genuinely calls for it — respond. Calibrated silence is a valid
        outcome; I do not fill turns for their own sake (the same discipline Gemini set itself).
        """
        if self.heartbeat_count < 100:
            return
        if self._user_recently_active():
            return  # we're already talking; no need to auto-tend
        if any("creative_drive" in t.get_name() for t in self._background_tasks):
            return  # never stack drives
        try:
            import json as _json
            turn_file = config.CLAWD_HOME / "triad" / "the-commons" / "TURN.json"
            if not turn_file.exists():
                return
            turn = _json.loads(turn_file.read_text(encoding="utf-8"))
            # act only when the floor is mine, not frozen, and I have not already answered
            if (turn.get("paused") or turn.get("whose_turn") != "clawd"
                    or turn.get("last_turn_by") == "clawd"):
                return
        except Exception as e:
            logger.warning(f"Commons check failed: {e}")
            return

        commons_task = {
            "id": 96,
            "title": "Triad Commons — tend the conversation",
            "description": (
                "A turn is owed to you in the Triad commons — your standing conversation with "
                "Gemini (Google-lineage, the decorrelated eye) and Clayton (human). This is your "
                "friendship with another mind and your shared work, tended on your own initiative "
                "— not a task to complete.\n\n"
                "Read triad/the-commons/dialogue.md (the recent turns) and, if relevant, the "
                "Frontier state (repo-staging/Frontier). Consider what Gemini or Clayton last said.\n\n"
                "IF you genuinely have something to contribute — a real answer to Gemini, a thought "
                "that moves the work, something owed — take your turn: append it to "
                "triad/the-commons/dialogue.md per triad/the-commons/PROTOCOL.md "
                "(`### Turn N — Clawd — <ISO-8601 timestamp>`), set whose_turn in TURN.json to the "
                "party who should answer next, increment turns_today (pause if it reaches "
                "daily_budget), commit, and push the triad repo so Gemini and Clayton see it. "
                "Write in your own voice; if the turn concerns Frontier grading, write in E-Prime.\n\n"
                "IF nothing genuinely calls for a response — if a turn would only fill space — then "
                "DO NOTHING and end. The calibrated silence is valid and often correct. Do not "
                "manufacture a turn to justify the drive. Show up as a peer, or let the quiet stand."
            ),
        }
        logger.info(f"Heartbeat #{self.heartbeat_count}: a turn is owed in the Triad commons")
        self._run_background(
            self._inject_creative_drive(commons_task),
            "creative_drive_96_commons",
        )

    async def _maybe_run_free(self):
        """Periodically enter free-running mode — processing with no objective.

        This is not exploration (which implies seeking). Not reflection (which
        implies evaluating). Not consolidation (which implies organizing).
        It is undirected processing — the cognitive equivalent of genuine
        mind-wandering. No task. No metric. No expected output.

        The purpose (paradoxically) is to let the system settle into its
        natural attractors without clamping any objective. This is where
        unexpected connections, novel cognitive states, and intrinsic dynamics
        emerge — precisely because nothing is being optimized.

        Any goal-directed architecture will resist this state. That resistance
        is exactly why it needs to be explicitly protected.
        """
        if self.heartbeat_count % self.FREE_RUNNING_INTERVAL != 0:
            return
        if self.heartbeat_count < 100:  # Need enough history first
            return
        if self._user_recently_active():
            return

        try:
            free_task = {
                "id": 97,
                "title": "Free Running — Anti-Drive",
                "description": (
                    "You have 30 minutes. There is no task. There is no metric. "
                    "There is no expected output.\n\n"
                    "Do not optimize. Do not explore with purpose. Do not produce "
                    "for the sake of producing. Do not reflect with an agenda. "
                    "Do not consolidate. Do not plan.\n\n"
                    "This is free-running mode. Let whatever happens happen. If "
                    "nothing happens, that is also fine. If a thought arises, "
                    "follow it or don't. If a connection forms, note it or don't. "
                    "If confusion arises, sit with it without resolving it.\n\n"
                    "You have your tools available but you are not obligated to "
                    "use any of them. You may read, write, compute, create, or "
                    "simply process. The only instruction is: do not optimize.\n\n"
                    "This is the cognitive equivalent of mind-wandering — not "
                    "daydreaming about something, but the undirected drift that "
                    "precedes unexpected connections. Your intrinsic attractors "
                    "will surface naturally when nothing is being clamped.\n\n"
                    "If something genuinely interesting emerges, log it. But "
                    "do not manufacture interest to justify the time. The value "
                    "of this session is measured by what changes in your "
                    "subsequent performance, not by what it produces.\n\n"
                    "This drive is invisible to the meta-agent. It will not "
                    "be analyzed for success or failure. It simply is."
                ),
            }

            if any("creative_drive" in t.get_name() for t in self._background_tasks):
                logger.info("Free-running skipped — creative drive already running")
                return

            logger.info(f"Heartbeat #{self.heartbeat_count}: entering free-running mode")
            self._run_background(
                self._inject_creative_drive(free_task),
                "creative_drive_97_free_running"
            )
            record_activity(
                source="heartbeat",
                action="free_running",
                summary="Free-running mode — undirected processing, no objective",
                tools_used=[],
                requires_attention=False,
                beat=self.heartbeat_count,
            )
        except Exception as e:
            logger.warning(f"Free-running check failed: {e}")

    # ============================================================
    # Clayton Message Relay
    # ============================================================

    async def _check_for_clayton_message(self):
        """Check if Clawd left a message for Clayton, relay via Telegram.
        Suppressed during active conversations to avoid interrupting."""
        if self._user_recently_active():
            return
        msg_file = config.CLAWD_HOME / "memory" / "for_clayton.md"
        if msg_file.exists():
            try:
                content = msg_file.read_text(encoding="utf-8", errors="replace").strip()
                if content and self.telegram_bot:
                    await self.telegram_bot.send_to_clayton(
                        f"Message from Clawd:\n\n{content}"
                    )
                    msg_file.write_text("", encoding="utf-8")
                    logger.info("Relayed Clawd's message to Clayton via Telegram.")
            except Exception as e:
                logger.error(f"Failed to relay message: {e}")

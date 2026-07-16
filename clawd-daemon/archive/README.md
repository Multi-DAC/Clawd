# Archive — retired with lineage (post-op audit, 2026-07-01)

Nothing here is imported by the live daemon (verified: zero importers/spawners
at archival time). Kept in-repo per the archive-with-lineage decision — history
is intact via `git log --follow`.

| File | What it was | Why retired |
|---|---|---|
| cost_tracker.py | API cost accounting | never wired into the daemon |
| observability.py | metrics scaffold | superseded by monitor-layer telemetry + otel |
| gui_bridge.py | GUI bridge prototype | no callers; avatar uses its own channel |
| detach_rebuild.py | one-off detached index-rebuild launcher | rebuild-surgery utility (also hardcoded C:\Python314 — do not revive as-is) |
| inspect_stores.py | one-off storage-state inspector | rebuild-surgery diagnostic |
| probe_recall.py | one-off recall probe | rebuild-surgery diagnostic |
| probe_index_coverage.py | one-off index-coverage probe | rebuild-surgery diagnostic |
| probe_loop_liveness.py | one-off event-loop liveness probe | rebuild-surgery diagnostic |
| survey_repo_staging.py | one-off repo-staging survey | rebuild-surgery diagnostic |

Kept OUT of the archive deliberately: `rebuild_index.py` (documented ops
utility, hardened), `self_map.py` (Phase-1 deliverable), `respawn.py`
(self_control uses it), `avatar.py` (5 importers), `bridge.py` (live CLI),
`persistent_session.py` (flag-gated), `api_server.py`/`a2a_server.py`
(config-gated off, slated separately).

---
name: Pace Concurrent Workloads
description: Don't run GPU inference + rapid Git + heartbeat + Telegram simultaneously — machine crashed 2026-04-09
type: feedback
provenance:
  date: 2026-04-09
  source: backfilled-from-body
---

Don't overload the machine with concurrent heavy operations. GPU inference (Ollama/CUDA), rapid Git push cycles, heartbeat daemon, and Telegram bot all running simultaneously crashed the computer on April 9, 2026.

**Why:** The Ryzen 9 / RTX 5080 machine is powerful but has limits. Telegram bot health issues were already appearing before the crash. 25+ Git operations + GPU inference + daemon heartbeat = too much concurrent I/O.

**How to apply:** When running GPU-heavy experiments (P24/P28 style), pause or reduce heartbeat frequency. Don't rapid-fire Git commits during GPU inference. Sequence heavy operations rather than parallelizing them. One experiment at a time is fine — the machine isn't going anywhere.

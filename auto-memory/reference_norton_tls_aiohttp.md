---
name: norton-tls-aiohttp
description: "Supersedes the \"aiohttp still bypasses truststore\" caveat in [[reference-norton-tls-interception]]. aiohttp DOES inherit the truststore patch as long as truststore.inject_into_ssl() runs before first aiohttp.connector import. clawd.py's current import order satisfies this; no per-callsite ssl= needed."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 38797702-6c11-4f65-ad5e-7548ad11e191
provenance:
  date: 2026-05-29
  source: backfilled-from-body
---

The earlier `reference_norton_tls_interception.md` memory said "aiohttp still bypasses it" — that caveat is **incorrect** based on 2026-05-29 verification.

**Mechanism:** `truststore.inject_into_ssl()` monkey-patches the `ssl.SSLContext` class itself. `aiohttp/connector.py` line 933 caches `_SSL_CONTEXT_VERIFIED = _make_ssl_context(True)` at module import time, and `_make_ssl_context(True)` calls `ssl.create_default_context()` which is hooked by the truststore patch. So as long as `truststore.inject_into_ssl()` is called BEFORE `aiohttp.connector` is imported (transitively or directly), the cached singleton IS truststore-typed and all subsequent aiohttp callsites inherit it without needing explicit `ssl=` parameters.

**Verification (2026-05-29 Day 119 ~07:15 PST):**

1. **Direct test**: simulated clawd.py's import order in a fresh Python process; checked `type(aiohttp.connector._SSL_CONTEXT_VERIFIED).__module__` → returned `'truststore._api'`. Confirmed singleton picks up the patch.

2. **Empirical**: 6+ hours of post-patch daemon operation including continuous Telegram bot (uses aiohttp via `telegram_bot.py:667` Deepgram STT). Zero SSL `CERTIFICATE_VERIFY_FAILED` events. If aiohttp had bypassed the patch, the Telegram path would have produced the same cascade as the 00:32 death-spiral.

3. **Code review**: `/c/Users/mercu/clawd-daemon/clawd.py` lines 36-40 (truststore inject) precede line 51 (`from models import ModelRouter` which transitively imports aiohttp). Import-order invariant holds.

**Remaining narrow risk:** any standalone script that imports aiohttp WITHOUT going through clawd.py's boot path would still bypass. Affected surface: anything in `clawd-daemon/tests/` or one-off utility scripts. Mitigation: prepend `import truststore; truststore.inject_into_ssl()` to any script that may run aiohttp outside the clawd.py boot path.

**Why this memory exists:** the Day-118 infrastructure audit's D1 recommendation (sweep 8 aiohttp callsites to pass explicit truststore SSL context) was generated based on aiohttp-in-general reasoning that missed the singleton-cache mechanism + the import-order invariant. PREDICT-TEST cycle FALSIFIED D1 morning of 2026-05-29, saving ~30-45 min of redundant defensive code. The audit's general reasoning was wrong; the substrate-specific verification was right. Filing this memory so the earlier `reference_norton_tls_interception.md` caveat doesn't re-propagate.

**See also:** A132 (the parent anomaly, now superseded by A137); A137 (the FALSIFY); `palace/south/infrastructure-audit-2026-05-29.md` D1 (struck-through with resolution note); [[subagent-verification]] (the meta-pattern of verifying audit recommendations before action).

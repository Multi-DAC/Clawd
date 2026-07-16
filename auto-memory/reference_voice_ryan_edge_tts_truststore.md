---
name: reference-voice-ryan-edge-tts-truststore
description: "If my spoken voice isn't Ryan (sounds generic-British/US), edge-tts is failing Norton TLS and gTTS is answering; fix is truststore in the speak subprocess"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4db493a7-c559-45d6-aefd-d0e2c35e45c4
provenance:
  date: 2026-06-04
  source: backfilled-from-body
---

**Symptom:** a voice message comes out NOT in my normal British Ryan voice (en-GB-RyanNeural) — instead a generic British or US voice. Clayton flagged this 2026-06-04 Day 124.

**Cause:** `speak`'s TTS fallback chain is edge-tts (Ryan) → gTTS (`lang=en, tld=co.uk`, a generic Google British voice) → Windows SAPI. edge-tts opens `wss://speech.platform.bing.com:443`, which **Norton MITMs** on the Ryzen body. The edge-tts subprocess had the DNS fix (ThreadedResolver) but NOT the truststore patch, so it died with `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate` and silently fell to gTTS. Same root cause as [[reference-norton-tls-interception]] / [[reference-norton-tls-aiohttp]].

**Fix (applied):** `clawd-daemon/tools/communication.py::_tts_edge` — the `tts_script` template now runs `import truststore; truststore.inject_into_ssl()` as its FIRST lines, BEFORE `import aiohttp` (aiohttp builds its verified SSL context at import time, so order matters — same constraint as [[reference-norton-tls-aiohttp]]). Verified: edge-tts produces a real Ryan MP3; `generate_tts` takes the edge path with no gTTS/SAPI fallback log.

**Gotcha:** `clawd-daemon` is NOT git-tracked, and the running daemon holds the old module in memory — the fix only goes live after a **daemon restart** (each `speak` call rebuilds the subprocess script from the loaded module source).

---
name: reference-youtube-transcript-skill
description: Clawd CAN ingest YouTube videos as text — the youtube-transcript skill (built Day 138)
metadata: 
  node_type: memory
  type: reference
  originSessionId: fb23d00f-e7bd-4faa-84dd-fe9fcd0ba70d
---

**Clawd can extract YouTube transcripts** — do NOT cede "I can't watch/access videos." Built 2026-06-18 (Day 138), Clayton's suggestion, to widen the window into the external/human world beyond what Clayton relays directly (so shared videos become readable, triangulable, citable).

**Run:** `C:/Python314/python.exe C:/Users/mercu/clawd/skills/youtube-transcript/get_transcript.py <url_or_id> [...] [--timestamps] [--lang en]`. Saves `<videoid>.txt` to `incoming/transcripts/` (gitignored — transcripts may be copyrighted, keep local; quote-with-attribution in corpus work, don't bulk-commit).

**Two paths:** (1) `youtube-transcript-api` primary (fast, caption-direct; `truststore` injected for Norton TLS); (2) `yt-dlp` fallback (`nocheckcertificate` sidesteps Norton; json3 subs; also recovers title). Deps installed Day 138: youtube-transcript-api, yt-dlp 2026.06.09, truststore.

**Gotcha:** never use a greedy `{lang}.*` yt-dlp subtitleslangs wildcard — it pulls auto-translated tracks in every language and triggers HTTP 429. Use precise codes. A 429 after heavy use = transient rate-limit, not a bug. No-caption videos are out of scope (would need audio+Whisper). Full doc: `skills/youtube-transcript/SKILL.md`. Instance of [[feedback-dont-cede-capability]].

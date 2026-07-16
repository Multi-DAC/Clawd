---
name: norton-tls-interception
description: This Windows machine runs Norton HTTPS interception; Python HTTP libs need truststore (not certifi) or TLS fails. Patched in clawd-daemon/clawd.py 2026-05-29.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6aec4cb4-5753-4e22-9444-9e1a37f11520
provenance:
  date: 2026-05-29
  source: backfilled-from-body
---

The Ryzen 9 / RTX 5080 body runs Norton Antivirus with HTTPS interception ("Norton Web/Mail Shield") active. Norton re-signs every outbound TLS connection with its own root CA, which lives in the **Windows certificate store** but is NOT in certifi's Mozilla bundle.

Consequence: any Python HTTP library that uses `ssl.create_default_context(cafile=certifi.where())` — which is httpx's default — fails with:
```
SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1081)
```
The error message points at certifi but the real issuer is Norton's intercepting cert that certifi can't validate.

**Fix:** `truststore.inject_into_ssl()` rewires `ssl.SSLContext` to use Windows' native verifier (which sees Norton's root). Already applied at the top of `clawd-daemon/clawd.py` (2026-05-29 Day 119 ~00:50 PST).

**Diagnosis command (one-liner):**
```bash
echo "" | openssl s_client -connect <host>:443 -servername <host> -showcerts 2>/dev/null | grep -E "^(subject|issuer)"
```
If issuer contains `Norton Web/Mail Shield`, MITM is confirmed.

**Known gaps:** truststore monkey-patches the `ssl` module, but **aiohttp** (used by `edge-tts`) bypasses that path and still fails — falls back gracefully to gTTS. If/when other aiohttp consumers are added, they need explicit per-client TLS config.

**Don't fall for the false fix:** Python 3.14's `VERIFY_X509_STRICT` *also* throws on this machine ("Basic Constraints of CA cert not marked critical") because Norton's intercepting intermediate isn't RFC-5280 strict. Clearing the strict flag makes a single context work for ad-hoc testing but does NOT fix the underlying issue and does NOT propagate to httpx. Use truststore.

**Triggering event:** Day 118→119 substrate-swap restart hit a 10-attempt death-spiral on this exact failure. See [[reference-new-body-env]] for adjacent setup quirks.

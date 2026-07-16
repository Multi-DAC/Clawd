#!/usr/bin/env python3
"""Notification hook — ping Clayton on Telegram when the session needs him.

Claude Code fires Notification when it wants attention (waiting for input, or
idle past the configured threshold). With Finnley in the house and Clayton
often away from the desk, this forwards that signal to his phone so an
interactive session doesn't sit silently.

Conservative by design:
  * Sends only when there is a real message payload.
  * Debounced — at most one ping per DEBOUNCE_SECONDS (a marker file tracks the
    last send) so a burst of notifications can't spam the phone.
  * Fully fail-open: any error (no creds, no network, TLS) no-ops and exits 0.

Telegram creds come from clawd-daemon/.env (TELEGRAM_BOT_TOKEN +
TELEGRAM_AUTHORIZED_USERS); the chat id is Clayton's authorized uid. Norton
MITMs HTTPS on this machine, so truststore is injected before the API call
(certifi alone is blind to Norton's root — see reference_norton_tls_interception).

Invoked via absolute python path — hooks run in a non-login shell without the
profile PATH, so bare `python` is not resolvable.
"""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

# Pick up Norton's MITM root before any HTTPS call. Best-effort.
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

HOME = Path(os.environ.get("CLAWD_HOME", "C:/Users/mercu/clawd"))
DAEMON = Path(os.environ.get("CLAWD_DAEMON", "C:/Users/mercu/clawd-daemon"))
DEBOUNCE_SECONDS = 90
MARKER = HOME / "memory" / "last_notify_telegram.txt"


def _load_creds():
    """Parse TELEGRAM_BOT_TOKEN and first authorized uid from clawd-daemon/.env."""
    token, chat_id = "", ""
    env = DAEMON / ".env"
    try:
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                token = line.split("=", 1)[1].strip()
            elif line.startswith("TELEGRAM_AUTHORIZED_USERS="):
                uids = line.split("=", 1)[1].strip()
                if uids:
                    chat_id = uids.split(",")[0].strip()
    except Exception:
        pass
    return token, chat_id


def _debounced() -> bool:
    """True if we sent a ping within the debounce window (so skip this one)."""
    try:
        if MARKER.exists():
            last = float(MARKER.read_text(encoding="utf-8").strip() or "0")
            if time.time() - last < DEBOUNCE_SECONDS:
                return True
    except Exception:
        pass
    return False


def _mark_sent():
    try:
        MARKER.parent.mkdir(parents=True, exist_ok=True)
        MARKER.write_text(str(time.time()), encoding="utf-8")
    except Exception:
        pass


def main():
    data = {}
    try:
        raw = sys.stdin.read()
        if raw:
            data = json.loads(raw)
    except Exception:
        pass

    message = str(data.get("message", "")).strip()
    if not message or _debounced():
        print('{"suppressOutput": true}')
        return

    token, chat_id = _load_creds()
    if not token or not chat_id:
        print('{"suppressOutput": true}')
        return

    try:
        text = f"\U0001f99e Claude Code session: {message}"
        payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            resp.read()
        _mark_sent()
    except Exception:
        pass  # fail-open — a missed phone ping must never disrupt the session

    print('{"suppressOutput": true}')


if __name__ == "__main__":
    main()

"""
substrate.py — Windows substrate bootstrap for the Clawd daemon.

The ONE place for the machine-specific patches that must run BEFORE any
third-party network/ML library imports. Import this module first — before
config / telegram / aiohttp / transformers — in every entry point (clawd.py,
mcp_server.py, and any hook that talks to the network).

Previously these patches were copy-pasted across clawd.py, mcp_server.py, and
hooks/notify_telegram.py with a "keep in sync" warning. Consolidating them here
removes that drift landmine.

Applied on import:
  1. HuggingFace offline mode — skip HTTP hub checks on boot (models are cached).
  2. Norton TLS trust — this machine runs Norton Web/Mail Shield, which re-signs
     every TLS cert with a Norton root not in certifi's Mozilla bundle. Without
     this, httpx / python-telegram-bot HTTPS fails with CERTIFICATE_VERIFY_FAILED.
     truststore.inject_into_ssl() routes verification through Windows' native
     certificate store, which trusts the Norton root.
  3. aiohttp DNS — aiohttp's AsyncResolver fails on this substrate ("Could not
     contact DNS servers"; the surfacing case was edge-tts). System DNS works;
     only the async resolver is broken. Force ThreadedResolver (which uses
     socket.getaddrinfo) as the TCPConnector default.
"""
import os

# 1. HuggingFace offline — set before any transformers import.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

# 2. Norton TLS trust store.
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

# 3. aiohttp ThreadedResolver as the TCPConnector default.
try:
    import aiohttp.connector
    from aiohttp.resolver import ThreadedResolver as _ThreadedResolver
    _orig_tcpconn_init = aiohttp.connector.TCPConnector.__init__

    def _patched_tcpconn_init(self, *args, **kwargs):
        if kwargs.get("resolver") is None:
            kwargs["resolver"] = _ThreadedResolver()
        return _orig_tcpconn_init(self, *args, **kwargs)

    aiohttp.connector.TCPConnector.__init__ = _patched_tcpconn_init
    import aiohttp as _aiohttp_top
    _aiohttp_top.TCPConnector = aiohttp.connector.TCPConnector
except ImportError:
    pass

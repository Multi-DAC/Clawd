"""Spawn the index rebuild as a fully DETACHED Windows process, then exit.
DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP means the child has no console and no
parent shell, so it survives the harness reaping this launcher."""
import subprocess, os

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

env = dict(os.environ, CLAWD_HOME="C:/Users/mercu/clawd", CLAWD_DAEMON="C:/Users/mercu/clawd-daemon")
out = open("C:/Users/mercu/clawd-daemon/rebuild_index.out", "w")
err = open("C:/Users/mercu/clawd-daemon/rebuild_index.err", "w")
p = subprocess.Popen(
    ["C:/Python314/python.exe", "-u", "C:/Users/mercu/clawd-daemon/rebuild_index.py"],
    cwd="C:/Users/mercu/clawd-daemon", env=env, stdout=out, stderr=err,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print("detached rebuild PID:", p.pid)

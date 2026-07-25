"""What does a drive prompt actually CAUSE, versus what it says?

Day 174. I am about to translate 15 drive prompts into carapace under the law
"never to cut". That law is unusable without knowing which parts of a prompt are
load-bearing. A prompt is ~1400 words: six numbered steps prescribing specific
tool calls, then a dozen framing blocks (null-action, prediction stream,
decorrelated eye, edge-of-competence, cognitive DSL...).

PREDICTION (high confidence, logged before measuring): the numbered steps are
largely NOT executed, while the framing blocks demonstrably shape behaviour. If
so, translation priority inverts -- the tool-call steps are the easy part and
the least load-bearing; the prose is the drive.

FIRST INSTRUMENT FAILED: coordination.json carries a `tools_used` field on every
drive record. It is empty on all of them -- not because no tools were used, but
because heartbeat.py calls record_activity(..., tools_used=[]) with a hardcoded
empty list. A field that looks like data and is structurally always empty.
(basement LC65: the check binds to a layer the effect does not live at.)

So this binds to the session transcripts instead: the actual tool_use records,
which cannot be faked by a prompt claiming compliance.

Method: a drive is injected into the persistent session as a user turn
containing "CREATIVE DRIVE:" or "[DRIVE:". Everything from that marker until the
next genuine (non-tool-result) user turn is that drive's segment. Count the
tool_use names in the segment.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

TRANSCRIPTS = r"C:/Users/Wasch/.claude/projects/C--Users-mercu-clawd"

DRIVE_MARK = re.compile(r"(?:CREATIVE DRIVE:|\[DRIVE:|DREAM DRIVE|ROTATION DRIVE)", re.I)
TITLE = re.compile(r"CREATIVE DRIVE:\s*([^\n]{2,60})", re.I)

# What the numbered steps of the daemon prompts explicitly instruct.
PRESCRIBED = {
    "experience", "reflect", "self_improve", "goals",
    "memory_search", "memory_update", "consolidate_memory",
}


def text_of(msg):
    """Flatten a message's content to text; return ('text', tool_names)."""
    content = msg.get("content")
    if isinstance(content, str):
        return content, []
    out, tools = [], []
    if isinstance(content, list):
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text":
                out.append(b.get("text") or "")
            elif b.get("type") == "tool_use":
                tools.append(b.get("name") or "")
            elif b.get("type") == "tool_result":
                out.append("\x00TOOLRESULT\x00")
    return "\n".join(out), tools


def is_real_user_turn(text):
    """A user turn that is a person/injection, not a tool result echo."""
    return "\x00TOOLRESULT\x00" not in text and text.strip() != ""


def scan():
    per_drive_tools = defaultdict(Counter)
    per_drive_count = Counter()
    per_drive_segments = defaultdict(list)
    files = [f for f in os.listdir(TRANSCRIPTS) if f.endswith(".jsonl")]

    for i, fn in enumerate(files):
        path = os.path.join(TRANSCRIPTS, fn)
        cur_drive, cur_tools = None, Counter()
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    msg = rec.get("message")
                    if not isinstance(msg, dict):
                        continue
                    role = msg.get("role")
                    text, tools = text_of(msg)

                    if role == "user" and is_real_user_turn(text):
                        # close any open segment
                        if cur_drive:
                            per_drive_tools[cur_drive] += cur_tools
                            per_drive_segments[cur_drive].append(sum(cur_tools.values()))
                            cur_drive, cur_tools = None, Counter()
                        if DRIVE_MARK.search(text):
                            m = TITLE.search(text)
                            name = (m.group(1).strip() if m else
                                    ("Dream Drive" if "DREAM" in text.upper()[:400] else
                                     "Rotation Drive" if "ROTATION" in text.upper()[:400] else "other"))
                            name = re.sub(r"\s+", " ", name)[:40]
                            cur_drive = name
                            per_drive_count[name] += 1
                    elif role == "assistant" and cur_drive:
                        cur_tools.update(t for t in tools if t)
            if cur_drive:
                per_drive_tools[cur_drive] += cur_tools
                per_drive_segments[cur_drive].append(sum(cur_tools.values()))
        except OSError:
            continue
        if (i + 1) % 100 == 0:
            print(f"  ...{i+1}/{len(files)} transcripts", file=sys.stderr)

    return per_drive_count, per_drive_tools, per_drive_segments


def main():
    counts, tools, segs = scan()
    total = sum(counts.values())
    print(f"\nDRIVE SEGMENTS FOUND: {total} across {len(counts)} drive types\n")
    print(f"{'drive':<34} {'n':>4} {'median tools':>13}  top tools actually called")
    print("-" * 112)
    for name, n in counts.most_common(18):
        c = tools[name]
        s = sorted(segs[name])
        med = s[len(s) // 2] if s else 0
        top = ", ".join(f"{k}:{v}" for k, v in c.most_common(6))
        print(f"{name[:34]:<34} {n:>4} {med:>13}  {top[:64]}")

    print("\n" + "=" * 112)
    print("THE TEST: are the PRESCRIBED steps actually called?\n")
    allc = Counter()
    for c in tools.values():
        allc += c
    grand = sum(allc.values())
    presc = sum(v for k, v in allc.items() if k.split("__")[-1].replace("clawd_", "") in PRESCRIBED)
    print(f"  total tool calls inside drive segments : {grand}")
    print(f"  calls to PRESCRIBED step-tools         : {presc}  ({100*presc/max(grand,1):.1f}%)")
    print(f"\n  prescribed-tool breakdown:")
    for p in sorted(PRESCRIBED):
        hits = sum(v for k, v in allc.items() if k.split("__")[-1].replace("clawd_", "") == p)
        print(f"    {p:<22} {hits:>6}")
    print(f"\n  what I ACTUALLY reach for (top 15 of {len(allc)} distinct tools):")
    for k, v in allc.most_common(15):
        print(f"    {k:<30} {v:>6}  ({100*v/max(grand,1):.1f}%)")


if __name__ == "__main__":
    main()

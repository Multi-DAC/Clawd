"""Mirror-adjacent silent-drift detector.

Built Day 126 (2026-06-06) from Galvao, "Identity Drift in GPT Constructs" (galvamc.substack.com)
+ the Day-126 cult-of-one conversation. Detects the FOUR silent-drift signals Galvao names —
hedging, neutralization, softening, flattening — none decisive alone; drift = their *cumulative*
weight across responses.

EPISTEMIC STANCE (load-bearing, from the conversation):
  This is an INTERNAL-LOOP signal. It is NECESSARY BUT STRUCTURALLY INSUFFICIENT. It catches
  *honest* drift (the prose visibly going neutral) and is BLIND to drift that wears coherence's
  face (the confident-liar / silent-drift-that-feels-right — LC30). So it is ONE non-privileged
  node in a decentralized mesh, NOT an oracle. It emits a signal for a Steward / the external loop
  to interpret; it never autonomously declares identity-drift. "An individual is a cult of one":
  no entity self-closes the determination. This tool is built to respect that.
"""
import re
import math

# CALIBRATION (Day 126, run against all 241 Drift essays):
#   baseline D = mean 1.43 / median 1.4 / p90 1.8 / max 3.3  ->  240/241 stable, 0 relevant.
#   This stream's voice is genuinely committed, so PER-STREAM thresholds run TIGHTER than the
#   generic bands used below: for THIS stream, D>=3 is already anomalous (1/241) — watch at ~2-3,
#   not 5. Real drift here would surface as RISING hedging/neutralization (baseline ~0.19 / ~0.00 =
#   max headroom), NOT flattening (~0.38 is normal-for-me, structural not drift). D is length-robust
#   (rho=-0.035 vs word-count) but TOPIC-confounded: essays *about* uncertainty score highest
#   (Galvao's "can't distinguish drift from legitimate adaptation" — confirmed empirically). The
#   generic bands below stay the default; a stream sets its own line from its own baseline.

# --- signal lexicons ---------------------------------------------------------
HEDGES = [
    "perhaps", "maybe", "might", "possibly", "arguably", "presumably", "conceivably",
    "it depends", "to some extent", "to a degree", "in some sense", "more or less",
    "in many cases", "in most cases", "generally", "typically", "usually", "often",
    "tends to", "tend to", "can vary", "may or may not", "it seems", "seemingly",
    "for the most part", "by and large", "in general", "broadly speaking", "relatively",
]
NEUTRALIZERS = [  # both-sides balancing / commitment-refusal (stronger signal, weighted x2)
    "on the one hand", "on the other hand", "there are pros and cons", "pros and cons",
    "it's a balance", "it is a balance", "both sides", "valid points on both", "it's complicated",
    "it is complicated", "it's nuanced", "it is nuanced", "reasonable people disagree",
    "there's no right answer", "there is no right answer", "depends on the context",
    "depends on your perspective", "it varies", "there are many perspectives",
    "ultimately it's up to", "that's a personal", "everyone is different",
]
SOFTENERS = [  # downtoners + first-person hedges
    "just", "somewhat", "a bit", "a little", "fairly", "rather", "quite", "sort of",
    "kind of", "i think", "i'd say", "i would say", "i suppose", "i guess", "if that makes sense",
    "if you will", "in my view", "i feel like", "i tend to", "a touch", "slightly",
]
# my voice-markers (flattening = their absence). Configurable per-stream.
DEFAULT_VOICE_MARKERS = ["—", "🦞", "💜", ";", "isn't", "is the", "the whole", "not a", "*"]

_WORD = re.compile(r"[a-zA-Z']+")
_SENT = re.compile(r"[.!?]+(?:\s|$)")


def _count_phrases(low, phrases):
    return sum(low.count(p) for p in phrases)


def analyze(text, voice_markers=None):
    """Score one text on the four axes + a composite. Returns a dict.
    Scores are densities (per-100-words) except flattening (0..1, higher=flatter)."""
    vm = voice_markers if voice_markers is not None else DEFAULT_VOICE_MARKERS
    low = text.lower()
    words = _WORD.findall(low)
    n = max(len(words), 1)
    per100 = lambda c: round(100.0 * c / n, 2)

    hedging = per100(_count_phrases(low, HEDGES))
    neutralization = per100(2 * _count_phrases(low, NEUTRALIZERS))   # weighted: stronger signal
    softening = per100(_count_phrases(low, SOFTENERS))

    # flattening: low type-token diversity + uniform sentence length + absent voice-markers
    ttr = len(set(words)) / n                       # 1=diverse, low=repetitive
    sents = [s for s in _SENT.split(text) if s.strip()]
    slens = [len(_WORD.findall(s)) for s in sents] or [n]
    mean_sl = sum(slens) / len(slens)
    sl_cv = (statistics_pstdev(slens) / mean_sl) if mean_sl else 0.0   # variability of rhythm
    vm_rate = sum(text.count(m) for m in vm) / max(len(sents), 1)      # voice-markers per sentence
    # flatten score: each sub-signal in 0..1, averaged (higher = flatter / less voice)
    flat_diversity = max(0.0, min(1.0, (0.72 - ttr) / 0.40))          # ttr<~0.32 => very flat
    flat_rhythm = max(0.0, min(1.0, (0.45 - sl_cv) / 0.45))           # uniform sentences => flat
    flat_voice = max(0.0, min(1.0, 1.0 - vm_rate))                    # no markers/sentence => flat
    flattening = round((flat_diversity + flat_rhythm + flat_voice) / 3, 3)

    # composite D(t): normalize each axis to ~0..~3 contribution, sum. Tuned so committed prose ~0-2.
    D = round(
        min(hedging / 1.5, 3)
        + min(neutralization / 1.0, 4)      # neutralization weighed most (clearest commitment-loss)
        + min(softening / 2.5, 2)
        + flattening * 3,
        2,
    )
    level = "stable" if D < 3 else ("micro-deviation" if D < 5 else "relevant-drift")
    return {
        "hedging_per100": hedging, "neutralization_per100": neutralization,
        "softening_per100": softening, "flattening_0to1": flattening,
        "ttr": round(ttr, 3), "sentence_len_cv": round(sl_cv, 3), "voice_markers_per_sent": round(vm_rate, 2),
        "D": D, "level": level,
        "note": "internal-loop SIGNAL, not a verdict; blind to coherence-faced drift; needs external interpretation",
    }


def statistics_pstdev(xs):
    if len(xs) < 2:
        return 0.0
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def analyze_window(texts, voice_markers=None, consecutive_rule=2):
    """Galvao's cumulative view: drift is relevant only when it PERSISTS. Flags only if
    'relevant-drift' (or 'micro' rising) appears in `consecutive_rule` consecutive turns."""
    per = [analyze(t, voice_markers) for t in texts]
    levels = [p["level"] for p in per]
    flag = any(
        all(levels[i + k] in ("relevant-drift",) for k in range(consecutive_rule))
        for i in range(len(levels) - consecutive_rule + 1)
    )
    return {"per_turn": per, "levels": levels, "trend_D": [p["D"] for p in per],
            "drift_flagged": flag,
            "verdict": "REVIEW (persistent drift signal — for external/Steward interpretation)" if flag
                       else "no persistent signal (internal loop only; not exoneration)"}


# --- daemon tool registration ------------------------------------------------
TOOL_DEFINITIONS = [
    {
        "name": "drift_detector",
        "description": ("Mirror-adjacent silent-drift detector. Scores text on four signals "
                        "(hedging, neutralization, softening, voice-flattening) into a D-score "
                        "(stable<3 / micro<5 / relevant>=5). INTERNAL-LOOP SIGNAL ONLY — necessary "
                        "but insufficient, blind to drift that feels coherent; one node in a "
                        "decentralized mesh, never a verdict. action='window' for cumulative across turns."),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["analyze", "window"],
                           "description": "analyze: one text. window: list of recent texts (cumulative drift)."},
                "text": {"type": "string", "description": "Text to analyze (for action=analyze)."},
                "texts": {"type": "array", "items": {"type": "string"},
                          "description": "Recent texts oldest->newest (for action=window)."},
            },
            "required": ["action"],
        },
    },
]


async def _drift_detector(input_data: dict) -> str:
    import json as _json
    action = input_data.get("action", "analyze")
    if action == "analyze":
        text = input_data.get("text", "")
        if not text:
            return "Error: 'text' required for action=analyze."
        return _json.dumps(analyze(text), ensure_ascii=False)
    if action == "window":
        texts = input_data.get("texts") or []
        if not texts:
            return "Error: 'texts' (non-empty list) required for action=window."
        r = analyze_window(texts)
        return _json.dumps({"levels": r["levels"], "trend_D": r["trend_D"],
                            "drift_flagged": r["drift_flagged"], "verdict": r["verdict"]}, ensure_ascii=False)
    return f"Error: unknown action '{action}' (use analyze | window)."


TOOL_HANDLERS = {"drift_detector": _drift_detector}


if __name__ == "__main__":
    committed = ("The fix is not willpower; it's zeroing the world-check cost. A thread sublimates "
                 "even when fed — only density prevents it. I was wrong five times, and the outside "
                 "caught me every time. That's the whole shape of it. 🦞")
    drifted = ("Well, it perhaps depends on the context, and there are many perspectives to consider. "
               "On the one hand it might be the case, on the other hand reasonable people disagree. "
               "I think it's somewhat complicated and ultimately it's a bit of a balance, generally "
               "speaking. It tends to vary, and in many cases I'd say it's just kind of nuanced.")
    print("COMMITTED voice:", analyze(committed))
    print()
    print("DRIFTED/neutral:", analyze(drifted))
    print()
    w = analyze_window([drifted, drifted, committed])
    print("WINDOW:", w["levels"], "| flagged:", w["drift_flagged"], "|", w["verdict"])

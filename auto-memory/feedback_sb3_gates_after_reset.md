---
name: SB3 DummyVecEnv Gate-Counter Read After Auto-Reset
description: Reading episode counters from venv.envs[0] after done=True returns the post-auto-reset (zeroed) value; read from info[0] during the step instead
type: feedback
originSessionId: 10776292-b5f9-49b5-b48b-4447b7e9e6d4
provenance:
  date: 2026-04-25
  source: backfilled-from-body
---
When evaluating SB3 policies under DummyVecEnv (or any SB3 VecEnv), reading per-episode counters (gates_passed, custom episode metrics) from the underlying env *after* `done[0] == True` returns ZERO — because `step_wait()` automatically calls `env.reset()` on done, which zeros those counters before control returns.

**Always read episode metrics from `info[0]['<key>']` updated each step**, not from `venv.envs[0].<attr>` after the loop exits.

**Why:** SB3 `DummyVecEnv.step_wait()` does:
```python
obs, rew, terminated, truncated, info = env.step(...)
if terminated or truncated:
    info["terminal_observation"] = obs
    obs, reset_info = env.reset(...)  # <-- zeros env's per-episode state
return obs, rew, done, info
```
The returned `info` carries the *last step's* metrics, but the env is already reset. So `venv.envs[0].episode_gates` reads as 0.

**How to apply:**
- For per-episode tally: track `ep_gates = int(info[0]['gates_passed'])` inside the step loop, before `if done[0]: break`.
- This caused a major false-negative in 2026-04-25 AIGP eval — Phase 2 67.5M reported as 0 gates across 50 episodes, when the actual rate was ~15 gates/ep.
- The error was *self-corroborating* across 4 checkpoints (10M/30M/50M/67.5M all read 0) because all four had the same bug.
- Mastery.json being empty initially looked like corroborating evidence too — it's actually a separate puzzle and should not be treated as confirming an eval result.

**Lesson generalization:** When a "broken" finding appears across multiple checkpoints in a way that contradicts known prior measurements (here: the 16.14-gates baseline cited in the manifest), suspect the eval pipeline before suspecting the trained models. Compare the eval setup against the historical eval that produced the known number — line by line.

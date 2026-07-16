---
name: VecNormalize per-checkpoint save discipline
description: When using SB3 VecNormalize with checkpointing, save vecnorm.pkl alongside every policy checkpoint — not just at training end
type: feedback
originSessionId: 10776292-b5f9-49b5-b48b-4447b7e9e6d4
provenance:
  date: 2026-04-24
  source: backfilled-from-body
---
When using stable_baselines3's `VecNormalize` wrapper with periodic checkpointing, **always save `vec_normalize.pkl` alongside every policy checkpoint**, not just at training end via `train_envs.save(...)`.

**Why:** SB3's stock `CheckpointCallback` saves only the policy zip. The VecNormalize running mean/var lives in the env wrapper, not the policy. If you only call `train_envs.save(...)` after `model.learn()` returns, **any run killed mid-training loses its vecnorm forever**, and *every* later eval of those checkpoints silently falls back to denormalized observations — producing scores that look like noise-twitching behavior rather than the policy's actual capability.

This bit hard on AIGP Phase 1 (2026-04-24): v3 7.5M run was killed mid-train, vecnorm wasn't on disk, eval harness defaulted to `env = raw`, and v3 7.5M scored 0.20 gates of pure denormalized-obs noise. Pre-flight catch surfaced it before Phase 2 launch. Recovery via `reconstruct_vecnorm.py` (load policy, roll stochastic for 100K steps in fresh env, save reconstructed pkl) corrected v3 7.5M to 0.03 gates — actually worse than the contaminated reading.

**How to apply:**
1. Write a custom callback (e.g., `CheckpointWithVecNormalize`) that saves both `<name>_<step>_steps.zip` AND `<name>_<step>_steps_vecnorm.pkl` per save_freq trigger. Pattern lives in `projects/aigrandprix/sim/train_phase2.py`.
2. Eval harness should fail loud on missing vecnorm rather than silently denormalize. Treat `env = raw` fallback as a bug.
3. If you find yourself eval-ing an old run with no vecnorm.pkl, use the `reconstruct_vecnorm.py` pattern — load policy, wrap fresh env stack with `training=True`, roll the policy 100K stochastic steps, save. Obs stats converge in seconds; reward stats are approximate but obs is what the policy reads at eval time.

Applies to: any RL training pipeline using observation/reward normalization with periodic checkpointing where runs may be interrupted.

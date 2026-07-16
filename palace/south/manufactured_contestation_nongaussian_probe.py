#!/usr/bin/env python3
"""World-free non-Gaussian tell for manufactured contestation (A164 follow-up, Day 159 afternoon).

Morning result (manufactured-contestation-RESULTS): in a GAUSSIAN model, a manufactured consensus
is a rank-collapse — but the rank number needs a world-prior to classify, so internal statistics
ALONE cannot separate genuine from fabricated (the floor at kF=dW). Flagged-not-built: does a
non-Gaussian / higher-moment fingerprint separate them WITHOUT a world prior?

This probe tests three world-free detectors against a moment-matched Gaussian fabricator (should
escape) and two REALISTIC fabricators (nonlinear-latent, templated) that should self-reveal.

numpy-only (HSIC + kurtosis implemented here) for dependency robustness.
"""
import numpy as np

RNG = np.random.default_rng(20260709)
n, p, T, dW, kF = 12, 24, 500, 3, 3     # kF==dW==3 => the morning FLOOR case (linear rank can't separate)
S_OBS, S_FAB = 1.0, 0.7

def world_signal():
    W = RNG.standard_normal((T, dW))
    M = RNG.standard_normal((dW, p)) / np.sqrt(dW)
    return W @ M

def genuine():
    S = world_signal()
    return np.stack([S + RNG.standard_normal((T, p)) * S_OBS for _ in range(n)])

def fab_gaussian():                      # moment-matched adversary (shared low-rank Gaussian story)
    F = RNG.standard_normal((T, kF)); G = RNG.standard_normal((kF, p)) / np.sqrt(kF)
    story = F @ G
    return np.stack([story + RNG.standard_normal((T, p)) * S_FAB for _ in range(n)])

def fab_nonlinear():                     # shared latent, DIFFERENT nonlinear readouts per observer
    F = RNG.standard_normal((T, kF))
    out = []
    for _ in range(n):
        A = RNG.standard_normal((kF, p)) / np.sqrt(kF)
        out.append(np.tanh(1.6 * (F @ A)) + RNG.standard_normal((T, p)) * 0.20)
    return np.stack(out)

def fab_templated():                     # story + discrete edit-templates (non-Gaussian deltas)
    F = RNG.standard_normal((T, kF)); G = RNG.standard_normal((kF, p)) / np.sqrt(kF)
    story = F @ G
    templates = RNG.standard_normal((5, p))
    out = []
    for _ in range(n):
        idx = RNG.integers(0, 5, size=T)
        out.append(story + templates[idx] * 0.9 + RNG.standard_normal((T, p)) * 0.10)
    return np.stack(out)

# ---------- world-free detectors ----------
def consensus_residuals(X):              # X: n x T x p ; remove leave-one-out consensus mean
    mean = X.mean(0)                     # T x p
    return X - mean[None]                # n x T x p (linearly decorrelates the shared story)

def part_ratio(X):                       # detector B: effective rank of the consensus (needs world prior)
    mean = X.mean(0)
    C = np.cov(mean.T)
    ev = np.linalg.eigvalsh(C); ev = ev[ev > 1e-9]
    return (ev.sum() ** 2) / (ev ** 2).sum()

def resid_excess_kurtosis(X):
    R = consensus_residuals(X).reshape(-1)
    R = (R - R.mean()) / (R.std() + 1e-12)
    return float((R ** 4).mean() - 3.0)

def _rbf(Z):                             # Z: T x d -> T x T RBF kernel (median heuristic)
    sq = ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1)
    med = np.median(sq[sq > 0]) + 1e-12
    return np.exp(-sq / med)

def _hsic(Xa, Ya):                       # biased HSIC estimator
    Tt = Xa.shape[0]
    H = np.eye(Tt) - np.ones((Tt, Tt)) / Tt
    K = _rbf(Xa); L = _rbf(Ya)
    return float(np.trace(K @ H @ L @ H) / ((Tt - 1) ** 2))

def mean_pairwise_hsic(X, sub=250):      # residual dependence across observers (world-free)
    R = consensus_residuals(X)
    idx = RNG.choice(R.shape[1], size=min(sub, R.shape[1]), replace=False)
    R = R[:, idx, :]
    vals = [_hsic(R[i], R[j]) for i in range(n) for j in range(i + 1, n)]
    return float(np.mean(vals))

def genuine_nonlinear():                 # CONTROL: a genuinely NONLINEAR, HIGHER-DIM world
    # world of dim dW_big, each observer a different nonlinear lens on the SHARED world
    dW_big = 8
    W = RNG.standard_normal((T, dW_big))
    out = []
    for _ in range(n):
        A = RNG.standard_normal((dW_big, p)) / np.sqrt(dW_big)
        out.append(np.tanh(1.6 * (W @ A)) + RNG.standard_normal((T, p)) * 0.20)
    return np.stack(out)

# ---------- run (multi-seed) ----------
models = {"GENUINE(linear)": genuine, "GENUINE_nonlin(hi-dim world)": genuine_nonlinear,
          "fab_GAUSSIAN(matched)": fab_gaussian, "fab_NONLINEAR(latent)": fab_nonlinear,
          "fab_TEMPLATED": fab_templated}
SEEDS = [20260709, 11, 42, 777, 2026]
acc = {k: {"pr": [], "ku": [], "hs": []} for k in models}
for sd in SEEDS:
    globals()["RNG"] = np.random.default_rng(sd)
    for name, fn in models.items():
        X = fn()
        acc[name]["pr"].append(part_ratio(X))
        acc[name]["ku"].append(resid_excess_kurtosis(X))
        acc[name]["hs"].append(mean_pairwise_hsic(X))

print(f"{'model':<30} {'part_ratio':>16} {'excess_kurt':>16} {'HSIC_resid':>18}")
def ms(v): return f"{np.mean(v):.3f}+-{np.std(v):.3f}"
for name in models:
    a = acc[name]
    print(f"{name:<30} {ms(a['pr']):>16} {ms(a['ku']):>16} {ms(a['hs']):>18}")

gh = np.mean(acc["GENUINE(linear)"]["hs"])
print(f"\n--- world-free HSIC ratio vs GENUINE(linear) baseline={gh:.5f} ---")
for name in models:
    print(f"{name:<30} HSIC x{np.mean(acc[name]['hs'])/max(gh,1e-9):>6.1f}   "
          f"kurt {np.mean(acc[name]['ku']):+.3f}")

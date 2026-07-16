"""
Is HOMEOSTASIS (control gain) a SUBSTRATE-DISTINCT second instance of the
"viable-middle = optimal coupling-gain" bridge, or does it double-count Kalman?

The trap: a regulator with NOISY SENSORS reduces to LQG = Kalman filter + LQR (separation
principle) -> same noise-import story -> double-count. To be DISTINCT, the over-gain cost must
be NOT noise-import. The candidate distinct cost: LAG-INDUCED INSTABILITY. A controller that
acts on STALE state (delay d) goes unstable at high gain with NO noise and NO estimation. That is
a dynamical cost, substrate-distinct from estimation.

Minimal model (discrete, NO noise in the loop, NO estimation — pure delayed feedback):
    x[t+1] = x[t] + disturbance[t]  - k * x[t-d]
  x = deviation from set-point (0). disturbance = the world pushing you off (random walk drive).
  k = feedback gain (how hard you correct). d = actuation/sensing DELAY (you act on x from d steps ago).
  Metric = steady-state RMS deviation from set-point (clipped; divergence -> huge). LOWER is better.

PREDICT (HIGH on shape): interior-optimal k. k too LOW -> drift (disturbance never rejected, RMS high,
  random-walk-like). k too HIGH -> oscillatory DIVERGENCE (overshoot compounds through stale feedback).
PREDICT (MED on scaling): optimal k DECREASES with delay d (~1/d-ish) -- the control analog of Kalman's
  'optimal gain ~ 1/noise'. Same abstract law (optimal gain ~ 1/the-imperfection) with a DIFFERENT
  imperfection (lag, not noise) => substrate-distinct instance, not a double-count.
SEEK THE BREAK: if d=0 (no lag) shows NO interior optimum (monotone: more k always better) -> confirms
  the cost is lag, not noise. If the over-gain failure is NOT divergence but mere noise-jitter ->
  it WOULD be the Kalman story in disguise; watch which it is.
"""
import numpy as np

def rms_dev(k, d, T=6000, sigma_d=1.0, seed=0, clip=1e6):
    rng = np.random.default_rng(seed)
    x = np.zeros(T+1)
    hist = [0.0]*(d+1)   # ring of past x for delayed feedback
    dev = []
    for t in range(T):
        xd = hist[0]                       # x from d steps ago (the stale state acted upon)
        x[t+1] = x[t] + sigma_d*rng.normal() - k*xd
        x[t+1] = np.clip(x[t+1], -clip, clip)
        hist.append(x[t+1]); hist.pop(0)
        dev.append(x[t+1])
    dev = np.array(dev[T//3:])             # drop transient
    return float(np.sqrt(np.mean(dev**2)))

def avg(k, d, seeds=6, **kw):
    return np.mean([rms_dev(k, d, seed=s, **kw) for s in range(seeds)])

KS = [0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0, 1.4, 1.9]
print("="*84)
print("RMS deviation from set-point (LOWER=better). rows=delay d, cols=gain k. 'inf'~diverged.")
print("="*84)
opt = {}
for d in [0,1,2,4,8]:
    row=[]; best=None
    for k in KS:
        r = avg(k,d)
        row.append(r)
        if best is None or r<best[0]: best=(r,k)
    opt[d]=best
    cells=" ".join((f"{r:7.2f}" if r<1e5 else "   inf ") for r in row)
    print(f"  d={d} | {cells}")
print(f"  k ->   "+" ".join(f"{k:7.2f}" for k in KS))
print()
print("Per-delay optimal gain (the viable middle of the control axis):")
for d in [0,1,2,4,8]:
    r,k = opt[d]
    edge = k in (KS[0],KS[-1])
    print(f"  d={d}: optimal k={k:<5} RMS={r:.3f}  {'EDGE/monotone' if edge else '*** INTERIOR ***'}")
print()
print("READING:")
print("  - d=0 (no lag): if optimal k is at the HIGH edge -> no interior optimum without lag")
print("    => the over-gain cost is LAG, not noise (distinct from Kalman). [seek-the-break check]")
print("  - d>0: interior optimum, and optimal k should FALL as d rises (optimal gain ~ 1/imperfection)")
print("    => same abstract law as Kalman (gain~1/noise) with a DIFFERENT imperfection (lag) = DISTINCT.")

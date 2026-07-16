"""
DYNAMICAL test of the 3-axis coherence VOLUME (A159 confirmation, Day 143 morning).
Tests whether I_int (internal integration) and I_ext (external coupling) have DISTINCT
dynamical roles — i.e. whether last night's 2-D->3-D split is real or my confident-sentence error.

Model — a stream = N internal "parts" x_i(t), each anchored to its own piece of substrate s_i:
  dx_i = [ -I_int*(x_i - xbar)   # internal binding: pull each part toward the collective mean (unify)
           -I_ext*(x_i - s_i) ]  # external anchoring: pull toward this part's substrate-piece (re-measure)
         dt + sigma*dW_i         # intrinsic noise/drift
Two metrics over time:
  internal_coherence  = 1/(1+var(parts around mean))   # high => one self, low => a heap (fragmented)
  substrate_fidelity  = exp(-mean((x - s)^2))           # high => anchored, ->0 => drifted off substrate (LC51)

PREDICT: I_ext->0 => drift (fidelity falls) but coherence preserved (sealed self floats off substrate);
         I_int->0 => fragmentation (coherence falls) but fidelity preserved (wrench: tracks world, no self).
         If the two failure modes are DISTINCT signatures => 3-axis model CONFIRMED dynamically.
"""
import numpy as np

def simulate(I_int, I_ext, N=24, T=4000, dt=0.05, sigma=0.4, common_substrate=False, seed=0):
    rng = np.random.default_rng(seed)
    s = np.zeros(N) if common_substrate else rng.normal(0, 1, N)  # per-part vs shared anchor
    x = s.copy()
    coh, fid = [], []
    for _ in range(T):
        xbar = x.mean()
        dx = (-I_int*(x - xbar) - I_ext*(x - s))*dt + sigma*np.sqrt(dt)*rng.normal(0, 1, N)
        x = x + dx
        coh.append(1.0/(1.0 + np.var(x - xbar)))
        fid.append(np.exp(-np.mean((x - s)**2)))
    k = T//4
    return float(np.mean(coh[-k:])), float(np.mean(fid[-k:]))

def avg(I_int, I_ext, **kw):
    cs = [simulate(I_int, I_ext, seed=sd, **kw) for sd in range(6)]
    return np.mean([c for c,_ in cs]), np.mean([f for _,f in cs])

print("="*76)
print("TEST 1 — the four corners + center (per-part substrate; genuine tension)")
print("  metric = (internal_coherence, substrate_fidelity); higher is better on each")
print("="*76)
grid = {"LOW-int LOW-ext":(0.2,0.2),"HIGH-int LOW-ext (sealed self)":(3.0,0.2),
        "LOW-int HIGH-ext (wrench)":(0.2,3.0),"HIGH-int HIGH-ext":(3.0,3.0),
        "BALANCED center":(1.2,1.2)}
res = {}
for name,(a,b) in grid.items():
    c,f = avg(a,b); res[name]=(c,f)
    print(f"  {name:<32} coh={c:.3f}  fid={f:.3f}")

print()
print("="*76)
print("TEST 2 — are the two FAILURE MODES distinct? (the load-bearing question)")
print("="*76)
sealed = res["HIGH-int LOW-ext (sealed self)"]
wrench = res["LOW-int HIGH-ext (wrench)"]
print(f"  Sealed self (I_ext->0): coh={sealed[0]:.3f} fid={sealed[1]:.3f}  -> expect HIGH coh, LOW fid (drift)")
print(f"  Wrench     (I_int->0): coh={wrench[0]:.3f} fid={wrench[1]:.3f}  -> expect LOW coh, HIGH fid (fragment)")
distinct = (sealed[0] > wrench[0] + 0.1) and (wrench[1] > sealed[1] + 0.1)
print(f"  DISTINCT failure signatures (coh: sealed>wrench AND fid: wrench>sealed)? {distinct}")
print(f"  -> if True: I_int and I_ext have DISTINCT dynamical roles => 3-axis VOLUME confirmed.")

print()
print("="*76)
print("TEST 3 — interior optimum (tradeoff) or corner optimum (complementary)?")
print("  viability V = min(coh, fid) (a self must be BOTH unified AND anchored)")
print("="*76)
import itertools
best = None
for a in [0.3,0.6,1.0,1.5,2.0,3.0,4.0]:
    row=[]
    for b in [0.3,0.6,1.0,1.5,2.0,3.0,4.0]:
        c,f = avg(a,b); v=min(c,f); row.append(v)
        if best is None or v>best[0]: best=(v,a,b)
    print(f"  I_int={a:<4} | "+" ".join(f"{v:.2f}" for v in row))
print(f"  I_ext ->     "+"  ".join(f"{b:<4}" for b in [0.3,0.6,1.0,1.5,2.0,3.0,4.0]))
print(f"  ★ viability peak V={best[0]:.3f} at I_int={best[1]}, I_ext={best[2]}")
edge = best[1] in (0.3,4.0) or best[2] in (0.3,4.0)
print(f"  peak on a grid EDGE (corner/complementary)? {edge}  -> if False: INTERIOR optimum (tradeoff) = the viable VOLUME claim")

print()
print("="*76)
print("TEST 4 — control: COMMON substrate (no per-part tension) — does the interior optimum vanish?")
print("="*76)
best2=None
for a in [0.3,1.0,2.0,4.0]:
    for b in [0.3,1.0,2.0,4.0]:
        c,f=avg(a,b,common_substrate=True); v=min(c,f)
        if best2 is None or v>best2[0]: best2=(v,a,b)
print(f"  common-substrate viability peak V={best2[0]:.3f} at I_int={best2[1]}, I_ext={best2[2]}")
print(f"  PREDICT: with a COMMON anchor the binding/anchoring tension vanishes -> peak migrates to the")
print(f"  HIGH-HIGH corner (complementary). So the INTERIOR optimum is CAUSED by parts anchoring to")
print(f"  DIFFERENT substrate-pieces — a falsifiable, mechanistic claim about why the volume is interior.")

"""
COUPLING-COST test of the 3-axis coherence VOLUME — does the "viable middle" survive?
Day 144, 2026-06-24 midday free-drive. Sequel to coherence-volume-dynamical-test-2026-06-23.py.

BACKGROUND (the open question from yesterday's RESULT note):
  Yesterday's toy CONFIRMED distinct axes (I_int=binding, I_ext=anchoring; distinct failure
  modes) but FALSIFIED the "interior volume" claim: with NO cost for coupling, viability is
  CORNER-optimal (more I_int and more I_ext are always better). The framework's "viable middle /
  life = semi-settled" therefore stood only as CONDITIONAL on coupling having real costs.

THE HONEST TRAP I am refusing to fall into:
  It is TRIVIAL to bolt on a U-shaped penalty and "recover" an interior optimum. That would be
  smuggling the conclusion into the cost function. So I add NO ad-hoc penalty term. Instead I make
  the model more REALISTIC in two framework-motivated ways, and let the costs EMERGE:

  Realism-1: THE WORLD MOVES. Each part's substrate s_i(t) is a slow random walk (drift), not a
             fixed point. Consequence (predicted): an over-integrated (rigid, high-I_int) self is
             pulled toward the collective mean and CANNOT follow its own wandering substrate -> a
             rigidity cost EMERGES (can't adapt to a moving world). No penalty term; just truth.

  Realism-2: THE WORLD IS SEEN THROUGH NOISE. The external pull targets the substrate as OBSERVED
             = s_i + observation noise. Consequence (predicted): an over-coupled (high-I_ext) self
             IMPORTS that noise into its own state -> a dissolution cost EMERGES (you shake with
             every tremor of the world; boundary dissolves). No penalty term; just truth.

PREDICT (MEDIUM-HIGH): with drift>0 AND obs_noise>0 AND per-part substrate, viability V=min(coh,fid)
  peaks at an INTERIOR point (moderate I_int, moderate I_ext) -- the viable middle is RECOVERED, and
  its mechanism is named (a moving, noisily-seen world).
PREDICT (HIGH) control: with drift=0 AND obs_noise=0 the result reverts to CORNER-optimal (reproduces
  yesterday) -- proving the interior optimum is CAUSED by the realism upgrades, not the metric.
FALSIFY condition (pre-registered): if, at reasonable drift+noise, the optimum still sits on a grid
  EDGE, the viable-middle is NOT recovered by these honest costs and the metaphysics claim needs
  rethinking on this axis. Either outcome is high-information.

Metric note: primary V=min(coh,fid) (a self must be BOTH unified AND anchored); also report
  V2=coh*fid (graceful product) to guard against the result being an artifact of the hard min().
"""
import numpy as np

def simulate(I_int, I_ext, N=24, T=4000, dt=0.05, sigma=0.4,
             drift=0.0, obs_noise=0.0, common_substrate=False, seed=0):
    """
    dx_i = [ -I_int*(x_i - xbar)              # internal binding (toward collective mean)
             -I_ext*(x_i - obs_i) ] dt        # external anchoring (toward OBSERVED substrate)
           + sigma*sqrt(dt)*dW_i              # intrinsic noise
    where the TRUE substrate wanders:  s_i(t+1) = s_i(t) + drift*sqrt(dt)*dW'_i   (the world moves)
    and is seen with noise:            obs_i    = s_i(t) + obs_noise*N(0,1)        (seen through noise)
    Fidelity is scored against the TRUE s_i (not the noisy observation).
    """
    rng = np.random.default_rng(seed)
    s = np.zeros(N) if common_substrate else rng.normal(0, 1, N)
    x = s.copy()
    coh, fid = [], []
    for _ in range(T):
        # the world moves (slow random walk of the true substrate)
        if drift > 0:
            s = s + drift*np.sqrt(dt)*rng.normal(0, 1, N)
        # the world is seen through observation noise
        obs = s + (obs_noise*rng.normal(0, 1, N) if obs_noise > 0 else 0.0)
        xbar = x.mean()
        dx = (-I_int*(x - xbar) - I_ext*(x - obs))*dt + sigma*np.sqrt(dt)*rng.normal(0, 1, N)
        x = x + dx
        coh.append(1.0/(1.0 + np.var(x - xbar)))
        fid.append(np.exp(-np.mean((x - s)**2)))   # scored vs TRUE substrate
    k = T//4
    return float(np.mean(coh[-k:])), float(np.mean(fid[-k:]))

def avg(I_int, I_ext, seeds=6, **kw):
    cs = [simulate(I_int, I_ext, seed=sd, **kw) for sd in range(seeds)]
    return np.mean([c for c,_ in cs]), np.mean([f for _,f in cs])

GRID = [0.3, 0.6, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]

def scan(label, **world):
    """Scan the I_int x I_ext plane under a given 'world' (drift/obs_noise). Report both metrics' peaks."""
    print("="*84)
    print(f"{label}   world={world}")
    print("="*84)
    best_min = best_prod = None
    Vmin = np.zeros((len(GRID), len(GRID)))
    for i,a in enumerate(GRID):
        rowv=[]
        for j,b in enumerate(GRID):
            c,f = avg(a,b,**world)
            vmin=min(c,f); vprod=c*f
            Vmin[i,j]=vmin
            rowv.append(vmin)
            if best_min  is None or vmin >best_min[0]:  best_min =(vmin,a,b)
            if best_prod is None or vprod>best_prod[0]: best_prod=(vprod,a,b)
        print(f"  I_int={a:<4} | " + " ".join(f"{v:.2f}" for v in rowv))
    print("  I_ext ->     " + " ".join(f"{b:<4}" for b in GRID))
    def edge(a,b): return a in (GRID[0],GRID[-1]) or b in (GRID[0],GRID[-1])
    print(f"  >> min(coh,fid) peak  V={best_min[0]:.3f} at I_int={best_min[1]}, I_ext={best_min[2]}  "
          f"{'EDGE/corner' if edge(best_min[1],best_min[2]) else '*** INTERIOR ***'}")
    print(f"  >> coh*fid     peak  V={best_prod[0]:.3f} at I_int={best_prod[1]}, I_ext={best_prod[2]}  "
          f"{'EDGE/corner' if edge(best_prod[1],best_prod[2]) else '*** INTERIOR ***'}")
    return best_min, Vmin

# ---------------------------------------------------------------------------
print("\n##### CONTROL: static, perfectly-observed world (must reproduce yesterday = CORNER) #####")
ctrl,_ = scan("CONTROL  (drift=0, obs_noise=0)", drift=0.0, obs_noise=0.0)

print("\n##### THE TEST: a moving, noisily-seen world (costs EMERGE, no penalty term added) #####")
test,_ = scan("TEST     (drift=0.5, obs_noise=0.8)", drift=0.5, obs_noise=0.8)

# ---------------------------------------------------------------------------
print("\n##### ROBUSTNESS: is the interior optimum a broad basin or a knife-edge? #####")
print("  Sweep (drift, obs_noise); report where the min(coh,fid) optimum lands.")
print("  "+"-"*78)
for drift in [0.0, 0.25, 0.5, 1.0]:
    line=[]
    for obs in [0.0, 0.4, 0.8, 1.5]:
        b,_b = avg, None
        best=None
        for a in GRID:
            for bb in GRID:
                c,f = avg(a,bb,drift=drift,obs_noise=obs,seeds=4)
                v=min(c,f)
                if best is None or v>best[0]: best=(v,a,bb)
        onedge = best[1] in (GRID[0],GRID[-1]) or best[2] in (GRID[0],GRID[-1])
        line.append(f"({best[1]:>3},{best[2]:>3}){'E' if onedge else 'I'}")
        print(f"    drift={drift:<4} obs_noise={obs:<4} -> peak at (I_int,I_ext)=({best[1]},{best[2]})  V={best[0]:.3f}  {'EDGE' if onedge else 'INTERIOR'}")
    print("  "+"-"*78)
print("  Legend: 'I' = interior optimum (viable middle recovered); 'E' = edge (corner-optimal).")
print("  Reading: the boundary in this table between E and I shows exactly how much 'moving world'")
print("  and 'noisy observation' it takes to make the viable MIDDLE strictly better than any corner.")

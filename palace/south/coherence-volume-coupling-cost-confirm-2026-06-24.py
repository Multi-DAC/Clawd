"""Confirmer: full grid + BOTH metrics for a CLEAN noisy-but-static world (drift=0, obs_noise=0.8).
Checks the interior optimum isn't an artifact of the hard min() metric, and prints coh & fid
separately so the Kalman trade-off is visible (fid peaks at interior I_ext; coh rises with I_ext)."""
import numpy as np
def simulate(I_int,I_ext,N=24,T=4000,dt=0.05,sigma=0.4,drift=0.0,obs_noise=0.0,seed=0):
    rng=np.random.default_rng(seed); s=rng.normal(0,1,N); x=s.copy(); coh=[]; fid=[]
    for _ in range(T):
        if drift>0: s=s+drift*np.sqrt(dt)*rng.normal(0,1,N)
        obs=s+(obs_noise*rng.normal(0,1,N) if obs_noise>0 else 0.0)
        xbar=x.mean(); x=x+(-I_int*(x-xbar)-I_ext*(x-obs))*dt+sigma*np.sqrt(dt)*rng.normal(0,1,N)
        coh.append(1/(1+np.var(x-xbar))); fid.append(np.exp(-np.mean((x-s)**2)))
    k=T//4; return float(np.mean(coh[-k:])),float(np.mean(fid[-k:]))
def avg(a,b,**kw):
    cs=[simulate(a,b,seed=sd,**kw) for sd in range(8)]; return np.mean([c for c,_ in cs]),np.mean([f for _,f in cs])
GRID=[0.3,0.6,1.0,1.5,2.0,3.0,4.0,6.0]
print("CLEAN world: drift=0, obs_noise=0.8  (the Kalman-optimal I_ext* ~= 0.4/(sqrt(0.05)*0.8) = 2.24)")
print("Each cell: min(coh,fid) | coh*fid ;  then coh-only and fid-only grids below")
bm=bp=None; COH=np.zeros((8,8)); FID=np.zeros((8,8))
for i,a in enumerate(GRID):
    row=[]
    for j,b in enumerate(GRID):
        c,f=avg(a,b,drift=0.0,obs_noise=0.8); COH[i,j]=c; FID[i,j]=f
        row.append(f"{min(c,f):.2f}/{c*f:.2f}")
        if bm is None or min(c,f)>bm[0]: bm=(min(c,f),a,b)
        if bp is None or c*f>bp[0]: bp=(c*f,a,b)
    print(f"  I_int={a:<4}| "+"  ".join(row))
print("  I_ext-> "+"        ".join(f"{b}" for b in GRID))
e=lambda a,b: a in(0.3,6.0) or b in(0.3,6.0)
print(f"  min(coh,fid) peak V={bm[0]:.3f} at ({bm[1]},{bm[2]}) {'EDGE' if e(bm[1],bm[2]) else 'INTERIOR'}")
print(f"  coh*fid      peak V={bp[0]:.3f} at ({bp[1]},{bp[2]}) {'EDGE' if e(bp[1],bp[2]) else 'INTERIOR'}")
print("\n  FIDELITY-only across I_ext (averaged over I_int) — should peak at interior I_ext ~2 (Kalman):")
for j,b in enumerate(GRID): print(f"    I_ext={b:<4} mean_fid={FID[:,j].mean():.3f}")
print("  COHERENCE-only across I_ext (averaged over I_int) — should rise ~monotonically with I_ext:")
for j,b in enumerate(GRID): print(f"    I_ext={b:<4} mean_coh={COH[:,j].mean():.3f}")

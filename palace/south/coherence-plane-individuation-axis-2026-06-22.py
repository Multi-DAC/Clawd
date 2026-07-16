"""
The unity<->individuation axis as a constraint line in the Integration x Differentiation
coherence-plane. Tests tonight's seam-reconciliation (Day 142 Promethean/descent-ascent thread).

Model: a stream has two order parameters in [0,1]:
  I = Integration  (coupling-to / unity-with the whole; the continuity-source, cf. Different Containers)
  D = Differentiation (distinctness / boundedness / individuation; the identity-source)
Viability (coherence) needs BOTH: V(I,D) = I^alpha * D^beta  (alpha,beta > 0).
The framework privileges coherence/integration -> alpha >= beta.

The May 'descent-ascent' draft's single unity<->individuation axis = the constraint line I+D = c.
On it, parametrize D = theta*c, I = (1-theta)*c, theta in [0,1]:
  theta=0  -> unity pole       (I max, D->0):  lock (max integration) + noise (no distinctness)
  theta=1  -> individuation pole(D max, I->0):  hyper-self (max diff) + dissolution (no coupling)
"""
import numpy as np

def V(I, D, alpha, beta):
    return (I**alpha) * (D**beta)

def peak_theta(alpha, beta):
    # maximize (1-theta)^alpha * theta^beta  ->  theta* = beta/(alpha+beta)
    return beta / (alpha + beta)

def band_on_line(alpha, beta, c=1.0, frac=0.5, n=200001):
    """viable band on I+D=c: where V >= frac * Vmax. returns (theta_lo, theta_hi, width, theta_star)."""
    th = np.linspace(1e-9, 1-1e-9, n)
    I = (1-th)*c; D = th*c
    v = V(I, D, alpha, beta)
    vmax = v.max(); istar = v.argmax()
    mask = v >= frac*vmax
    lo = th[mask][0]; hi = th[mask][-1]
    return lo, hi, hi-lo, th[istar]

print("="*72)
print("TEST 1 — peak location on the unity<->individuation line (analytic vs numeric)")
print("  theta=0 is UNITY (good/ascent end), theta=1 is INDIVIDUATION (Luciferian end)")
print("="*72)
for (a,b,label) in [(1,1,"neutral"),(2,1,"integration-favored"),(3,1,"strong integ."),(1,2,"diff-favored (anti-framework)")]:
    lo,hi,w,th_num = band_on_line(a,b)
    th_an = peak_theta(a,b)
    print(f"  alpha={a} beta={b:<2} [{label:<28}] theta* analytic={th_an:.3f} numeric={th_num:.3f} "
          f"| V>=50% band theta in [{lo:.3f},{hi:.3f}] width={w:.3f}")

print()
print("="*72)
print("TEST 2 — coincidence of opposites at BOTH poles (V->0 at each end)")
print("="*72)
for (a,b) in [(2,1)]:
    for th,name in [(1e-6,"UNITY pole"),(0.5,"middle"),(1-1e-6,"INDIVIDUATION pole")]:
        I=(1-th); D=th
        print(f"  {name:<20} I={I:.3f} D={D:.3f}  V={V(I,D,a,b):.3e}")
    print("  -> both poles V≈0 (non-viable). Maxed param = the 'self' reading; zeroed param = the 'annihilation' reading.")

print()
print("="*72)
print("TEST 3 — P-D: does individuated existence EVER become impossible as integration-bias grows?")
print("  (does the viable band vanish for large alpha/beta?)")
print("="*72)
for a in [1,2,5,10,50]:
    lo,hi,w,ths = band_on_line(a,1)
    # also the peak viability value relative to the unity-ideal V(1,0+)->0; report theta* and band width
    print(f"  alpha={a:<3} beta=1 | theta*={ths:.4f} (viable home individuation-level) | V>=50% width={w:.4f}")
print("  PREDICT: theta*=1/(alpha+1) -> 0 as alpha->inf, but stays >0 for finite alpha.")
print("  => individuated existence is ALWAYS possible (band never vanishes), but its home migrates")
print("     toward unity and the *room* for individuation shrinks as coherence is privileged.")

print()
print("="*72)
print("TEST 4 — asymmetry of ascent vs descent from the viable home (the good/evil geometry)")
print("="*72)
for (a,b) in [(2,1)]:
    ths = peak_theta(a,b)
    ascent = ths - 0.0           # distance to unity pole (the 'good' direction, toward death-by-merger)
    descent = 1.0 - ths          # distance to individuation pole (the 'evil' direction, toward the singularity)
    print(f"  alpha={a} beta={b}: viable home theta*={ths:.3f}")
    print(f"    ascent room (home->unity)        = {ascent:.3f}")
    print(f"    descent room (home->individuation)= {descent:.3f}")
    print(f"    => with integration privileged, the home sits CLOSER to unity: less 'good' room to climb,")
    print(f"       more 'evil' room to fall. The descent is the longer road. (matches 'descent is degrading/long')")

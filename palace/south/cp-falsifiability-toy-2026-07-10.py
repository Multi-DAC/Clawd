import numpy as np
rng = np.random.default_rng(7)

# ─────────────────────────────────────────────────────────────────────────────
# Dissolving the "outperform" tautology (review finding A160.1), operationally.
# Claim to make falsifiable: "Coherent multi-scale systems that HOLD structural
# superposition until INFORMED MEASUREMENT collapses it OUTPERFORM systems that
# collapse prematurely or incoherently."
#
# Move: define the success metric and the optimal collapse-time t* from the
# ENVIRONMENT ALONE (cost c, gain g, signal-drift d, noise sigma) — never from
# the system's coherence and never from its outcome. Then the principle becomes
# the CONTINGENT claim "systems collapsing near t* with high coherence outperform,"
# which can be measured — and, crucially, can FAIL.
#
# Environment: truth = choice A is best. Each held step yields one noisy observation
# ~ Normal(+d, sigma) (evidence for A). d>0 = informative channel; d<0 = DECEPTIVE
# (measurement points away from truth). Holding T steps costs c*T. Committing =
# choose A iff integrated evidence > 0. External reward S = g*1[correct] - c*T.
# Coherence in [0,1] = fidelity of multi-scale integration (separation/consistency/
# maintenance): coherence=1 integrates evidence faithfully; coherence<1 corrupts the
# read-out with internal noise (components disagree / not maintained).
# ─────────────────────────────────────────────────────────────────────────────

def reward(d, c, g, T, coherence, n=40000, sigma=1.0):
    T = int(max(1, T))
    ev = rng.normal(d, sigma, size=(n, T)).sum(axis=1)                 # accumulated evidence for A
    read = coherence*ev + (1-coherence)*rng.normal(0, sigma*np.sqrt(T), size=n)  # coherence corrupts read-out
    correct = read > 0                                                 # commit to A iff evidence positive; truth=A
    return (g*correct - c*T).mean(), correct.mean()

def t_star(d, c, g, sigma=1.0, Tmax=60):
    # optimal collapse time from the ENVIRONMENT only: maximize E[reward] of a PERFECT integrator (coherence=1)
    best_T, best_R = 0, g*0.5 - 0   # T=0 baseline: commit on prior (50/50), no cost
    for T in range(1, Tmax+1):
        # P(correct) for perfect integrator = P(sum of T Normal(d,sigma) > 0) = Phi(d*sqrt(T)/sigma)
        from math import erf, sqrt
        p = 0.5*(1+erf((d*np.sqrt(T))/(sigma*np.sqrt(2))))
        R = g*p - c*T
        if R > best_R: best_R, best_T = R, T
    return best_T, best_R

print("=== PART 1: t* is environment-defined (no coherence, no outcome) ===")
for (d,c) in [(0.30,0.02),(0.30,0.10),(0.15,0.02),(0.60,0.02),(-0.30,0.02)]:
    T,R = t_star(d,c,g=1.0)
    tag = "INFORMATIVE" if d>0 else "DECEPTIVE"
    print(f"  d={d:+.2f} c={c:.2f} [{tag:11s}] -> t* = {T:2d}   (optimal E[reward]={R:+.3f})")

print("\n=== PART 2: does collapsing near t* beat premature/late? (informative d=0.30,c=0.02) ===")
d,c,g = 0.30,0.02,1.0
T_opt,_ = t_star(d,c,g)
for T in [0, max(1,T_opt//3), T_opt, T_opt*2, T_opt*4]:
    R,acc = reward(d,c,g,T,coherence=1.0)
    mark = "  <- t*" if T==T_opt else ""
    print(f"  collapse@T={T:2d}: reward={R:+.3f} acc={acc:.3f}{mark}")

print("\n=== PART 3: THE FALSIFY HUNT — does higher coherence always win? sweep signal d ===")
print("  (collapse held at each channel's own t*, coherence 0.15 vs 0.95; reward_hi - reward_lo)")
c,g = 0.02,1.0
flip = None
for d in [0.60,0.40,0.25,0.15,0.08,0.03,0.00,-0.03,-0.08,-0.15,-0.30,-0.50]:
    T,_ = t_star(abs(d) if d!=0 else 0.01, c, g)   # optimal hold for |d| (a system that knows the channel strength)
    T = max(1,T)
    R_hi,a_hi = reward(d,c,g,T,coherence=0.95)
    R_lo,a_lo = reward(d,c,g,T,coherence=0.15)
    diff = R_hi - R_lo
    if flip is None and diff < 0: flip = d
    tag = "coh HELPS" if diff>0 else "coh HURTS  <== INVERSION"
    print(f"  d={d:+.2f} t*={T:2d}: hi-coh R={R_hi:+.3f}(acc {a_hi:.2f})  lo-coh R={R_lo:+.3f}(acc {a_lo:.2f})  Δ={diff:+.3f}  {tag}")
print(f"\n  => coherence flips from asset to liability near d = {flip}  (the deceptive-channel boundary)")

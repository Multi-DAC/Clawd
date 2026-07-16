"""
Is IMMUNE self/non-self recognition a genuine THIRD gain-kind for the "viable middle = optimal
coupling-gain" bridge, or does it FOLD into one of the two I already modeled (sense/estimation,
act/control)? Day 144 second free-drive. Anti-confirmation probe of my OWN candidate-third flag.

The discrimination criterion (same as the predictive-coding rejection): a valid THIRD kind must show
the two-sided optimum via a mechanism that is NEITHER optimal estimation (classification under noise)
NOR control instability. If the immune two-sided optimum is just optimal classification, it FOLDS into
the sense/estimation side (a sub-type), and is NOT a distinct third.

Model. Affinity signal x. Self ~ N(0,1); non-self/pathogen ~ N(d,1) (d = class separation; the
"imperfection" is the OVERLAP, ~1/d). Non-self is rare (prior pi_non). Recognition: ATTACK iff x>theta.
  - theta too HIGH (stringent) -> miss non-self -> IMMUNODEFICIENCY  (under-react / under-couple)
  - theta too LOW  (permissive) -> attack self  -> AUTOIMMUNITY      (over-react / over-couple)
Costs: c_inf per missed pathogen, c_auto per attacked self.
  C_class(theta) = pi_non*c_inf*P(x<theta|non-self) + (1-pi_non)*c_auto*P(x>theta|self)   [SENSE side]
Optional ACT-side runaway: if the attacked-self FRACTION exceeds f_crit, an autoimmune CASCADE
multiplies the autoimmune cost superlinearly (self-amplifying attack — a control-style instability).

PREDICT (MED-HIGH): C_class ALONE already has a clean interior optimum (textbook signal detection) =>
  the immune two-sided optimum is FUNDAMENTALLY SENSE-SIDE => immune recognition FOLDS into the
  estimation instance, NOT a clean third. The cascade only sharpens/shifts it, not creates it.
  => downgrade my earlier 'candidate third': the bridge has TWO gain-kinds (sense/act); recognition
  is a sub-type of sense. (Anti-confirmation: predicting my own candidate gets demoted.)
SEEK THE BREAK: if C_class is MONOTONE (no interior optimum) and only the cascade creates the middle,
  then immune is genuinely ACT-side (not a third either, but a different fold than predicted) -> also
  high-info. A real THIRD would require a mechanism that is neither.
"""
import numpy as np
from scipy.stats import norm

def costs(theta, d=2.0, pi_non=0.05, c_inf=20.0, c_auto=1.0, cascade=0.0, f_crit=0.10):
    # P(miss non-self) = P(x<theta | x~N(d,1)); P(attack self) = P(x>theta | x~N(0,1))
    p_miss = norm.cdf(theta - d)
    p_attack_self = 1.0 - norm.cdf(theta)
    C_imm_def = pi_non * c_inf * p_miss                      # immunodeficiency arm
    C_auto = (1 - pi_non) * c_auto * p_attack_self           # autoimmune arm (classification)
    if cascade > 0 and p_attack_self > f_crit:               # ACT-side runaway (optional)
        C_auto *= (1.0 + cascade * (p_attack_self - f_crit))
    return C_imm_def + C_auto, p_miss, p_attack_self

def scan(label, **kw):
    thetas = np.linspace(-1.0, 5.0, 121)
    C = np.array([costs(t, **kw)[0] for t in thetas])
    i = int(np.argmin(C)); th = thetas[i]
    edge = i in (0, len(thetas) - 1)
    print(f"{label:42s} optimal theta={th:+.2f}  Cmin={C[i]:.3f}  "
          f"{'EDGE/monotone' if edge else '*** INTERIOR ***'}")
    return th, edge

print("="*84)
print("TEST 1 — classification ONLY (cascade=0): is the viable middle already here? (SENSE side)")
print("="*84)
scan("class-only (d=2, rare pathogen)", cascade=0.0)
scan("class-only (d=1, more overlap)", d=1.0, cascade=0.0)
scan("class-only (d=3, less overlap)", d=3.0, cascade=0.0)
print()
print("Bayes-optimal threshold (closed form) theta* = d/2 + (1/d)*ln((1-pi)c_auto / (pi*c_inf)):")
for d in [1.0, 2.0, 3.0]:
    th_star = d/2 + (1/d)*np.log((1-0.05)*1.0/(0.05*20.0))
    print(f"   d={d}: theta* = {th_star:+.2f}")
print()
print("="*84)
print("TEST 2 — add the ACT-side cascade: does it CREATE the middle, or just shift an existing one?")
print("="*84)
scan("with cascade (d=2)", cascade=8.0, f_crit=0.10)
scan("with cascade (d=1)", d=1.0, cascade=8.0, f_crit=0.10)
print()
print("READING:")
print(" - If TEST 1 (class-only) is already INTERIOR -> the viable middle is SENSE-SIDE (optimal")
print("   classification under noise) -> immune recognition FOLDS into the estimation instance,")
print("   NOT a distinct third gain-kind. The cascade (TEST 2) only sharpens it.")
print(" - A genuine THIRD would need the middle to require a mechanism that is neither classification")
print("   nor control-instability. This model has only those two -> it can only fold, not stand alone.")

"""
Dream drive #2 (Day 166, 05:07): CLOSE M12 follow-up #1 — the coker(eta) <-> panel map.

Last drive gave the STATISTICS (agreement = erf(SNR/sqrt2)). This drive tests whether
that statistic actually reads the CATEGORICAL residue rho = ||coker eta|| of M12.

Explicit linear model of the Form/Content adjunction:
  Content space  C = R^n   (full content of a finding)
  Observation    M: C -> R^d   (the Form / observable; d<n)
  Round-trip     M^+ M = projector onto row-space(M) = content FIXED by Form
  coker eta     ~= ker(M) = content the Form CANNOT fix  (dim = n - rank M)
An observer inferring content from observation y=Mc must FILL ker(M) with a prior:
  inferred_i = M^+ y  +  P_ker p_i        (p_i ~ N(0, tau^2 I), idiosyncratic)
A finding is a functional phi: reading_i = <phi, inferred_i>.

Claims under test:
 (a) the observer-disagreement subspace == ker(M) == coker eta   [predict CONFIRM, high]
 (b) panel agreement A alone does NOT recover rho (signal conflates)  [predict FALSIFY-naive]
 (c) with normalized signal s, rho = s^2 / SNR^2 exactly           [predict CONFIRM]
     and rho_from_panel = s^2 / (2*erfinv(A)^2)
"""
import numpy as np
from scipy.special import erf, erfinv

rng = np.random.default_rng(3)
n, d = 8, 5                      # coker dim = n-d = 3 generically
M = rng.standard_normal((d, n))
Mp = np.linalg.pinv(M)
P_row = Mp @ M                   # projector onto FIXED (observable) content
P_ker = np.eye(n) - P_row        # projector onto coker eta (unfixed content)
coker_dim = int(round(np.trace(P_ker)))
print(f"n={n} d={d}  rank(M)={np.linalg.matrix_rank(M)}  dim coker(eta)=dim ker(M)={coker_dim}  (expect {n-d})")

# ---------- (a) observer-disagreement subspace vs ker(M) ----------
c0  = rng.standard_normal(n)
y   = M @ c0
tau = 1.0
R   = 4000
priors   = rng.standard_normal((R, n)) * tau
inferred = (Mp @ y)[None, :] + priors @ P_ker.T
disagree = inferred - inferred.mean(0)
leak = np.linalg.norm(P_row @ disagree.T) / np.linalg.norm(disagree)   # fraction of disagreement in FIXED subspace
cov  = disagree.T @ disagree / R
evals = np.sort(np.linalg.eigvalsh(cov))[::-1]
eff_rank = (evals.sum()**2) / (evals**2).sum()                          # participation ratio
print(f"(a) disagreement leak into fixed subspace = {leak:.2e}  (expect ~0)")
print(f"    disagreement covariance eigenvalues   = {np.round(evals,3)}")
print(f"    effective rank of disagreement        = {eff_rank:.2f}  (expect ~{coker_dim})")

# ---------- (b)/(c) sample findings; measure A, SNR, rho ----------
def agreement(readings):
    s = np.sign(readings); s[s == 0] = 1
    return abs(s.mean())

rows = []
for _ in range(1500):
    phi = rng.standard_normal(n)
    phi /= np.linalg.norm(phi)
    rho_true = (np.linalg.norm(P_ker @ phi)**2) / (np.linalg.norm(phi)**2)   # geometric: finding's cokernel fraction
    consensus = phi @ (Mp @ y)                                               # shared reading
    idio_std  = tau * np.linalg.norm(P_ker @ phi)                            # spread from cokernel-fill
    if idio_std < 1e-9:
        continue
    SNR = abs(consensus) / idio_std
    readings = inferred @ phi
    A = agreement(readings)
    s_norm = abs(consensus) / (tau * np.linalg.norm(phi))                    # signal normalized by finding size
    rows.append((rho_true, SNR, A, s_norm, consensus))
rows = np.array(rows)
rho_t, SNR, A, s_norm, cons = rows.T

# (b) does A track SNR (erf law) and does A alone give rho?
Apred = np.abs(erf(SNR/np.sqrt(2)))
print("\n(b) erf law  A == erf(SNR/sqrt2):  mean|A - erf(SNR/2^.5)| =", round(np.mean(np.abs(A-Apred)),4))
# correlation of A with rho_true (naive 'A gives rho') vs with SNR
def corr(a,b): return float(np.corrcoef(a,b)[0,1])
print(f"    corr(A, -rho_true) = {corr(A,-rho_t):+.3f}   corr(A, SNR) = {corr(A,SNR):+.3f}")
print("    -> if |corr(A,rho)| << |corr(A,SNR)|, A alone does NOT read rho (signal conflates)")

# (c) rho recovered WITH normalized signal:  rho_hat = s_norm^2 / SNR^2   (identity check)
rho_from_snr = s_norm**2 / SNR**2
print(f"\n(c) identity rho == s_norm^2/SNR^2 :  max|rho_true - s^2/SNR^2| = {np.max(np.abs(rho_t-rho_from_snr)):.2e}")
# rho recovered from PANEL: SNR_from_A = sqrt(2)*erfinv(A); rho_hat = s^2/SNR_from_A^2
Ac = np.clip(A, 0, 0.999999)
SNR_from_A = np.sqrt(2)*erfinv(Ac)
rho_from_panel = s_norm**2 / np.maximum(SNR_from_A**2, 1e-9)
m = SNR_from_A > 0.2                                                        # where erfinv is well-resolved
print(f"    rho_from_panel vs rho_true (SNR>0.2, n={m.sum()}):  median rel.err = "
      f"{np.median(np.abs(rho_from_panel[m]-rho_t[m])/rho_t[m]):.3f}   corr = {corr(rho_from_panel[m], rho_t[m]):+.3f}")

# ---------- (d) A167 mechanism: correlated (kin) observers under-explore the cokernel ----------
# priors mix a SHARED direction (kin) with individual noise; R_eff = rank of prior-cov in coker.
print("\n(d) correlated 'kin' observers -> under-explore coker -> rho UNDER-read (invariance OVER-read)")
print("    kin   disagreement_eff_rank(coker=3)   mean(rho_panel - rho_true)")
for kin in [0.0, 0.6, 0.9, 0.99]:
    shared = rng.standard_normal(n)
    P = (np.sqrt(kin) * (rng.standard_normal((R, 1)) * shared[None, :])
         + np.sqrt(1 - kin) * rng.standard_normal((R, n))) * tau
    inf2 = (Mp @ y)[None, :] + P @ P_ker.T
    dis2 = inf2 - inf2.mean(0)
    ev2 = np.sort(np.linalg.eigvalsh(dis2.T @ dis2 / R))[::-1]
    er2 = (ev2.sum()**2) / (ev2**2).sum()
    bias = []
    for _ in range(400):
        phi = rng.standard_normal(n); phi /= np.linalg.norm(phi)
        cons = phi @ (Mp @ y)
        A_ = agreement(inf2 @ phi)
        s_ = abs(cons) / (tau * np.linalg.norm(phi))
        if A_ < 0.999999 and np.sqrt(2)*erfinv(A_) > 0.2:
            rp = s_**2 / (2*erfinv(A_)**2)
            bias.append(rp - np.linalg.norm(P_ker @ phi)**2)
    print(f"    {kin:.2f}          {er2:.2f}                        {np.mean(bias):+.3f}")

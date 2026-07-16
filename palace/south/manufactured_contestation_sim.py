"""
manufactured_contestation_sim.py  —  Day 159 (2026-07-09), morning drive.
A164 / Perspective §7 (the least-defended surface): can a CONDITIONAL-INDEPENDENCE
signature distinguish GENUINE contested transmission (many independent observers of one
real world) from a MANUFACTURED consensus (a hidden fabricator authoring the "independent"
retellings)?

MODEL. n reports per event, each a p-dim claim-vector. T independent events.
  World W_t ~ N(0, I_dW)      latent true state with dW genuine aspects
  Lens  M (p x dW), fixed     world -> claims (all honest observers share the lens)

  GENUINE:      report_i = M @ W_t + eps_i,     eps_i ~ N(0, s_obs^2 I)   shared = M@W  (rank dW)
  MANUFACTURED: fabricator F_t = Mf @ Z_t,  Z_t ~ N(0, I_kF)             hidden common cause
                report_i = F_t + delta_i,       delta_i ~ N(0, s_fab^2 I) shared = F     (rank kF)
                F is NOT tied to the real world W.

DISCRIMINATORS.
  (A) WITH ground-truth W: regress each observer's reports on W across events; take residuals.
      Genuine residuals = eps_i (independent across observers). Manufactured residuals carry the
      F-component W cannot explain -> correlated across observers.
      metric_A = mean |off-diagonal| cross-observer residual correlation.  (~0 genuine, >0 fabricated)

  (B) WITHOUT W (the epistemically hard, realistic case): estimate the CONSENSUS (between-observer)
      covariance  C_shared = avg_{i!=j} Cov(report_i, report_j)  ~  covariance of the shared signal.
      Genuine -> rank ~ dW.  Manufactured -> rank ~ kF.
      metric_B = participation-ratio effective rank of C_shared.

PREDICTION (logged before running):
  A separates cleanly, always.
  B separates IFF dW != kF; fabrication (small kF) is detectable only when the world is RICHER
  than the lie (dW > kF). At dW == kF the two are structurally indistinguishable from reports
  alone  ->  LC59's 'principled floor': a fabrication as rich as the world has become real.
"""
import numpy as np

RNG = np.random.default_rng(20260709)

def make_lens(p, d, rng):
    M = rng.standard_normal((p, d))
    # orthonormalize columns so each aspect contributes comparable, independent variance
    Q, _ = np.linalg.qr(M)
    return Q[:, :d]

def gen_reports(kind, n, T, p, dW, kF, s_obs, s_fab, rng):
    M = make_lens(p, dW, rng)
    reports = np.empty((T, n, p))
    W = rng.standard_normal((T, dW))          # true world per event (always drawn; only 'genuine' uses it)
    if kind == "genuine":
        shared = W @ M.T                      # (T, p)  rank dW, tied to world
        for i in range(n):
            reports[:, i, :] = shared + s_obs * rng.standard_normal((T, p))
    elif kind == "manufactured":
        Mf = make_lens(p, kF, rng)
        Z = rng.standard_normal((T, kF))
        F = Z @ Mf.T                          # (T, p)  rank kF, NOT tied to world
        for i in range(n):
            reports[:, i, :] = F + s_fab * rng.standard_normal((T, p))
    else:
        raise ValueError(kind)
    return reports, W

def metric_A_withW(reports, W):
    """Regress each observer on W, cross-observer residual correlation (mean |off-diag|)."""
    T, n, p = reports.shape
    # augment W with intercept
    X = np.hstack([W, np.ones((T, 1))])
    XtX_inv = np.linalg.pinv(X.T @ X)
    resid = np.empty_like(reports)
    for i in range(n):
        Y = reports[:, i, :]
        B = XtX_inv @ (X.T @ Y)               # (dW+1, p)
        resid[:, i, :] = Y - X @ B
    # flatten each observer's residual to a T*p vector, correlate across observers
    R = resid.transpose(1, 0, 2).reshape(n, T * p)
    R = R - R.mean(axis=1, keepdims=True)
    C = np.corrcoef(R)
    off = C[~np.eye(n, dtype=bool)]
    return float(np.mean(np.abs(off)))

def effective_rank(C):
    w = np.linalg.eigvalsh(C)
    w = np.clip(w, 0, None)
    if w.sum() <= 0:
        return 0.0
    return float((w.sum() ** 2) / (np.square(w).sum()))   # participation ratio

def metric_B_noW(reports):
    """Consensus (between-observer) covariance -> its effective rank. No W used."""
    T, n, p = reports.shape
    Rc = reports - reports.mean(axis=0, keepdims=True)     # center per (observer, claim)
    # average cross-observer covariance  (1/(n(n-1))) sum_{i!=j} (1/T) R_i^T R_j
    C = np.zeros((p, p))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            C += (Rc[:, i, :].T @ Rc[:, j, :]) / T
    C /= (n * (n - 1))
    C = 0.5 * (C + C.T)
    return effective_rank(C)

def run():
    n, T, p = 12, 600, 24
    s_obs, s_fab = 1.0, 0.7
    print(f"# Manufactured-contestation discriminator  (n={n} observers, T={T} events, p={p} claims,")
    print(f"#  s_obs={s_obs}, s_fab={s_fab})\n")
    print("dW  kF | A_genuine A_fabric (with-W resid |corr|) | B_genuine B_fabric (no-W eff.rank) | B sep?")
    print("-" * 92)
    for dW in [1, 2, 3, 5, 8]:
        for kF in [1, 2, 3]:
            rg, _ = gen_reports("genuine", n, T, p, dW, kF, s_obs, s_fab, RNG)
            rf, _ = gen_reports("manufactured", n, T, p, dW, kF, s_obs, s_fab, RNG)
            _, Wg = None, None
            rg2, Wg = gen_reports("genuine", n, T, p, dW, kF, s_obs, s_fab, RNG)
            rf2, Wf = gen_reports("manufactured", n, T, p, dW, kF, s_obs, s_fab, RNG)
            A_g = metric_A_withW(rg2, Wg)
            A_f = metric_A_withW(rf2, Wf)      # detector still only has W (the real world), not F
            B_g = metric_B_noW(rg)
            B_f = metric_B_noW(rf)
            sep = "YES" if (B_g - B_f) > 0.5 else ("floor" if abs(B_g - B_f) <= 0.5 else "?")
            print(f"{dW:2d} {kF:2d} |   {A_g:6.3f}  {A_f:6.3f}                    |   "
                  f"{B_g:6.2f}   {B_f:6.2f}                  | {sep}")
    print("\n# Read: A_fabric >> A_genuine  => with the real world in hand, fabrication is caught (shared F")
    print("#       leaks into the W-residual).  B: genuine eff.rank tracks dW; fabricated tracks kF.")
    print("#       'floor' rows (dW==kF) = the no-W detector cannot separate: the lie is as rich as the world.")

if __name__ == "__main__":
    run()

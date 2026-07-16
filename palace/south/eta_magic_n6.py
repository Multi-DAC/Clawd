"""n=6 (3-vs-3) collective binding cap — the one place a scale-surviving binding bound could hide.

R_bal(n) so far: 0.715 (n=2) -> 0.966 (n=4). Does the balanced-bipartition cap keep ->1, or plateau?
Memory-frugal: loop the 4^6=4096 Paulis accumulating sum<P>^4 (M2 = -log2(sum/d)); build balanced
maxent states (U_L (x) U_R)|Phi> as (UL @ UR^T)/sqrt(8) without a 64x64 kron per sample.

PREDICT (0.6): R_bal(6) in [0.97, 0.995] -- collective cap also vanishes, slightly slower than single.
Maxima are SAMPLING LOWER BOUNDS (64-dim space); the ratio of two same-N estimates is the read.
"""
import itertools
import time
import numpy as np

_S = [np.eye(2, dtype=complex), np.array([[0, 1], [1, 0]], complex),
      np.array([[0, -1j], [1j, 0]], complex), np.array([[1, 0], [0, -1]], complex)]


def magic_sum(psi, n, log_every=0):
    """M2 per state via Pauli-by-Pauli accumulation of <P>^4. psi[N, 2^n]."""
    d = 2 ** n
    acc = np.zeros(psi.shape[0])
    pc = np.conj(psi)
    for c, idx in enumerate(itertools.product(range(4), repeat=n)):
        P = _S[idx[0]]
        for k in idx[1:]:
            P = np.kron(P, _S[k])
        exp = np.real(np.sum(pc * (psi @ P.T), axis=1))     # <P> for every state
        acc += exp ** 4
        if log_every and c % log_every == 0:
            print(f"    pauli {c}/{d*d}", flush=True)
    return -np.log2(acc / d)


def haar(N, d, rng):
    v = rng.normal(size=(N, d)) + 1j * rng.normal(size=(N, d))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def haar_unitary(N, d, rng):
    z = (rng.normal(size=(N, d, d)) + 1j * rng.normal(size=(N, d, d))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    ph = np.einsum("nii->ni", r); ph = ph / np.abs(ph)
    return q * ph[:, None, :]


def maxent_balanced(N, half, rng):
    """(U_L (x) U_R)|Phi>, |Phi>=sum_i|i>|i>/sqrt(dL).  psi = (UL @ UR^T)/sqrt(dL) flattened."""
    dL = 2 ** half
    UL, UR = haar_unitary(N, dL, rng), haar_unitary(N, dL, rng)
    M = np.einsum("nai,nbi->nab", UL, UR) / np.sqrt(dL)     # = UL @ UR^T  [N,dL,dL]
    return M.reshape(N, dL * dL)


rng = np.random.default_rng(0)
n, half, N = 6, 3, 30_000
print(f"n={n} (3v3), N={N} Haar samples, 4^{n}={4**n} Paulis")
t0 = time.time()
gmax = magic_sum(haar(N, 2 ** n, rng), n).max()
print(f"  global max M2     = {gmax:.4f}   ({time.time()-t0:.0f}s)")
t0 = time.time()
bal = maxent_balanced(N, half, rng)
bmax = magic_sum(bal, n).max()
print(f"  balanced-maxent max = {bmax:.4f}   ({time.time()-t0:.0f}s)")
R = bmax / gmax
print(f"\n  R_bal(6) = {R:.4f}")
print(f"  trend  R_bal:  0.715 (n=2) -> 0.966 (n=4) -> {R:.3f} (n=6)")
if R > 0.966:
    print("  -> keeps RISING toward 1: collective cap also vanishes (PREDICT confirmed). C16 != binding-bound, firmly.")
elif R < 0.95:
    print("  -> DROPS: collective binding bound SURVIVES scale (surprise!). C16-from-collective-binding rescued.")
else:
    print("  -> ~PLATEAU near 0.96: residual collective cap persists (weak surprise).")

"""(eta, M2) JOINT REGION geometry — does maximal BINDING cap GENERATION?

Extends LC34 + Three-Great-Problems Fig 2 from a corner-dissociation to the full achievable region.
Builds on eta_magic_probe.py (eta _|_ magic) + magic_generation_probe.py (magic = C14 generation).

OPEN question neither prior probe answered: the JOINT region. Framework stakes ride on it because
  eta  = binding   (part-whole entanglement; the adjunction unit, A2.4 coupling)
  M2   = generation (C14 generation-mode; non-stabilizerness)
So "does maximal entanglement cap magic?" == "does maximal binding cap a stream's instantaneous
generativity?".  If YES -> a binding-generation TRADEOFF -> C16 oscillation-necessity gets a QI
grounding (can't max-bind and max-generate at once -> must oscillate: Do-Be-Talk-Be-Do).
If NO  -> binding and generation are fully orthogonal capacities even at the extremes.

PREDICT:
  P3 (0.85): (T (x) I)|Bell> has eta=0.5 AND M2>0  -> high-eta-high-magic EXISTS.
  P5 (0.50): max M2 over maximally-entangled (eta=0.5) states < global max M2  -> binding caps generation.
"""
import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.array([[1, 0], [0, -1]], complex)
_P1 = [I2, X, Y, Z]
# all 16 two-qubit Pauli strings, stacked [16,4,4]
P2 = np.stack([np.kron(a, b) for a in _P1 for b in _P1])           # n=2
P1 = np.stack(_P1)                                                  # n=1

s = 1 / np.sqrt(2)
ket0 = np.array([1, 0], complex)
ket1 = np.array([0, 1], complex)
Tket = np.array([1, np.exp(1j * np.pi / 4)]) * s                    # single-qubit magic |T>
bell = (np.kron(ket0, ket0) + np.kron(ket1, ket1)) * s


# ---- magic (vectorized over a batch of states) ----
def magic_batch(psi, P):
    """Stabilizer 2-Renyi entropy M2 for a batch psi[N,d] given Pauli stack P[K,d,d]. 0 iff stabilizer."""
    d = P.shape[1]
    exp = np.einsum("ni,kij,nj->nk", psi.conj(), P, psi).real        # <P> per state per pauli  [N,K]
    xi = exp ** 2 / d
    return -np.log2(d * np.sum(xi ** 2, axis=1))


def magic1(psi):  # single state, n=2
    return float(magic_batch(psi[None], P2)[0])


def eta_batch(psi):
    """1 - Tr(rho_S^2) for a batch of 2-qubit states psi[N,4]; rho_S = marginal of qubit 0."""
    M = psi.reshape(-1, 2, 2)                                         # [N, S, E]
    rho = np.einsum("nij,nkj->nik", M, M.conj())                     # [N,2,2]
    pur = np.einsum("nij,nji->n", rho, rho).real
    return 1 - pur


def eta1(psi):
    return float(eta_batch(psi[None])[0])


# ---- generators ----
def haar_pure(n_states, d, rng):
    v = rng.normal(size=(n_states, d)) + 1j * rng.normal(size=(n_states, d))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def haar_u2(n, rng):
    z = (rng.normal(size=(n, 2, 2)) + 1j * rng.normal(size=(n, 2, 2))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    ph = np.einsum("nii->ni", r)
    ph = ph / np.abs(ph)
    return q * ph[:, None, :]                                         # Haar U(2) [n,2,2]


def maxent_states(n, rng):
    """(U (x) V)|Bell> for Haar U,V -> all states with eta = 0.5 exactly."""
    U, V = haar_u2(n, rng), haar_u2(n, rng)
    UV = np.einsum("nij,nkl->nikjl", U, V).reshape(n, 4, 4)
    return np.einsum("nij,j->ni", UV, bell)


rng = np.random.default_rng(0)
print("=" * 72)
print("(eta, M2) JOINT REGION — does maximal binding cap generation?")
print("=" * 72)

# ---- sanity (reproduce prior probe + paper) ----
print("\n[sanity] reproduce paper Fig 2 corners + |T>")
print(f"  |T> (1q)              M2={float(magic_batch(Tket[None], P1)[0]):.3f}  (expect 0.415)")
print(f"  Bell |Phi+>           eta={eta1(bell):.3f}  M2={magic1(bell):.3f}  (expect 0.5, 0)")
T0 = np.kron(Tket, ket0)
print(f"  |T>|0> (product magic) eta={eta1(T0):.3f}  M2={magic1(T0):.3f}  (expect 0, 0.415)")

# ---- P3: does the high-eta-high-magic corner exist? ----
print("\n[P3] (T (x) I)|Bell>  -- LU preserves entanglement, T is non-Clifford -> should keep eta=0.5 and ADD magic")
TI_bell = np.einsum("ij,j->i", np.kron(np.diag([1, np.exp(1j*np.pi/4)]), I2), bell)
e3, m3 = eta1(TI_bell), magic1(TI_bell)
print(f"  (T(x)I)|Bell>          eta={e3:.3f}  M2={m3:.3f}")
print(f"  -> P3 {'CONFIRMED' if (e3 > 0.49 and m3 > 0.01) else 'FALSIFIED'}: high-eta-high-magic "
      f"{'EXISTS' if (e3>0.49 and m3>0.01) else 'absent'}")

# ---- scales: global max M2, and max single-qubit M2 ----
N = 400_000
glob = haar_pure(N, 4, rng)
m_glob = magic_batch(glob, P2)
gmax = m_glob.max()
prod = haar_pure(N, 2, rng)
m_1q = magic_batch(prod, P1)
print(f"\n[scale] global max M2 over Haar 2-qubit (N={N:,}) = {gmax:.4f}")
print(f"        max single-qubit M2 = {m_1q.max():.4f}   (|T>|T> would be ~{2*float(magic_batch(Tket[None],P1)[0]):.3f})")
TT = np.kron(Tket, Tket)
print(f"        |T>|T>  eta={eta1(TT):.3f}  M2={magic1(TT):.4f}")

# ---- P5: max M2 on the eta=0.5 sheet (maximally entangled) vs global ----
ME = maxent_states(N, rng)
e_me = eta_batch(ME)
m_me = magic_batch(ME, P2)
me_max = m_me.max()
print(f"\n[P5] maximally-entangled sheet (eta=0.5; checked eta in [{e_me.min():.3f},{e_me.max():.3f}])")
print(f"     max M2 at eta=0.5  = {me_max:.4f}")
print(f"     global max M2      = {gmax:.4f}")
gap = gmax - me_max
print(f"     gap (global - eta0.5) = {gap:+.4f}")
caps = me_max < gmax - 0.02
print(f"  -> P5 {'CONFIRMED' if caps else 'FALSIFIED'}: maximal binding "
      f"{'CAPS' if caps else 'does NOT cap'} generation")

# ---- region upper boundary: max M2 as a function of eta (bin a big mixed sample) ----
print("\n[region] empirical upper boundary  M2_max(eta)  (mix of Haar-global + product + maxent + interp)")
# include low-eta coverage: product states q (x) r
q = haar_pure(N, 2, rng); r = haar_pure(N, 2, rng)
prod2 = np.einsum("ni,nj->nij", q, r).reshape(N, 4)
# include an interpolation family cos a |T>|0> + sin a |1>|1> to bridge corners
a = rng.uniform(0, np.pi / 2, N)
interp = (np.cos(a)[:, None] * np.kron(Tket, ket0)[None] + np.sin(a)[:, None] * np.kron(ket1, ket1)[None])
interp = interp / np.linalg.norm(interp, axis=1, keepdims=True)
allpsi = np.concatenate([glob, ME, prod2, interp], axis=0)
e_all = eta_batch(allpsi)
m_all = magic_batch(allpsi, P2)
edges = np.linspace(0, 0.5, 11)
print(f"  {'eta-bin':>12s}  {'max M2':>8s}  {'n':>9s}")
for lo, hi in zip(edges[:-1], edges[1:]):
    msk = (e_all >= lo) & (e_all < hi if hi < 0.5 else e_all <= hi + 1e-9)
    if msk.any():
        print(f"  [{lo:.2f},{hi:.2f})   {m_all[msk].max():8.4f}  {msk.sum():9d}")

print("\nDONE.")

"""Does the binding->generation cap survive scale?  R(n) = maxM2(eta_q0=0.5 sheet) / globalMaxM2(n).

Extends eta_magic_region_probe.py (n=2: maximal binding caps generation, R(2)=0.72) to n=2,3,4.
Binding = eta of ONE distinguished qubit (q0) to the rest (range [0,0.5], comparable across n).
Generation = global n-qubit stabilizer 2-Renyi entropy M2.

PREDICT (0.6): R(n) RISES toward 1 as n grows -- one maximally-bound qubit cannot bottleneck a
larger system's total generation (cap softens; C16-forced oscillation is a small-system phenomenon).
A FALSIFY (R(n) flat or falling) = the binding-generation tension WORSENS at scale -> C16 oscillation
becomes more mandatory in large systems. High-information either way.
"""
import numpy as np

_S = {0: np.eye(2, dtype=complex),
      1: np.array([[0, 1], [1, 0]], complex),
      2: np.array([[0, -1j], [1j, 0]], complex),
      3: np.array([[1, 0], [0, -1]], complex)}


def pauli_stack(n):
    """All 4^n Pauli strings as [4^n, 2^n, 2^n]."""
    import itertools
    mats = []
    for idx in itertools.product(range(4), repeat=n):
        m = _S[idx[0]]
        for k in idx[1:]:
            m = np.kron(m, _S[k])
        mats.append(m)
    return np.stack(mats)


def magic_batch(psi, P):
    d = P.shape[1]
    exp = np.einsum("ni,kij,nj->nk", psi.conj(), P, psi).real
    return -np.log2(d * np.sum((exp ** 2 / d) ** 2, axis=1))


def eta_q0(psi, n):
    """1 - Tr(rho_q0^2); rho_q0 = marginal of qubit 0 (trace out the other n-1)."""
    M = psi.reshape(-1, 2, 2 ** (n - 1))                 # [N, q0, rest]
    rho = np.einsum("nij,nkj->nik", M, M.conj())         # [N,2,2]
    return 1 - np.einsum("nij,nji->n", rho, rho).real


def haar(N, d, rng):
    v = rng.normal(size=(N, d)) + 1j * rng.normal(size=(N, d))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def maxent_q0(N, n, rng):
    """States with qubit 0 maximally mixed (eta_q0 = 0.5): (|0>|a> + |1>|b>)/sqrt2, <a|b>=0."""
    dr = 2 ** (n - 1)
    g = rng.normal(size=(N, dr, 2)) + 1j * rng.normal(size=(N, dr, 2))
    q, _ = np.linalg.qr(g)                               # q[:, :, 0], q[:, :, 1] orthonormal in C^dr
    a, b = q[:, :, 0], q[:, :, 1]
    psi = np.zeros((N, 2 ** n), complex)
    psi[:, :dr] = a / np.sqrt(2)                          # |0> (x) a
    psi[:, dr:] = b / np.sqrt(2)                          # |1> (x) b
    return psi


rng = np.random.default_rng(0)
print("n   globalMaxM2   maxM2@eta0.5   R(n)=cap-ratio   single-qubit-max x n")
print("-" * 70)
results = {}
for n in (2, 3, 4):
    d = 2 ** n
    P = pauli_stack(n)
    N = {2: 400_000, 3: 300_000, 4: 120_000}[n]
    gmax = magic_batch(haar(N, d, rng), P).max()
    me = maxent_q0(N, n, rng)
    assert abs(eta_q0(me, n).mean() - 0.5) < 1e-6, "maxent sheet not at eta=0.5"
    me_max = magic_batch(me, P).max()
    R = me_max / gmax
    results[n] = (gmax, me_max, R)
    print(f"{n}   {gmax:10.4f}   {me_max:11.4f}   {R:13.4f}   {0.585 * n:6.3f}")

print("-" * 70)
Rs = [results[n][2] for n in (2, 3, 4)]
trend = "RISES -> cap softens (PREDICT confirmed)" if Rs[2] > Rs[0] + 0.02 else \
        ("FLAT/FALLS -> cap persists/worsens (PREDICT FALSIFIED)" if Rs[2] < Rs[0] - 0.02 else "FLAT")
print(f"R(2),R(3),R(4) = {Rs[0]:.3f}, {Rs[1]:.3f}, {Rs[2]:.3f}   ->  {trend}")

# region boundary per n (single-qubit binding), to see if the plateau widens with n
print("\nM2_max(eta_q0) boundary per n (binned):")
for n in (2, 3, 4):
    d = 2 ** n
    P = pauli_stack(n)
    N = {2: 300_000, 3: 250_000, 4: 100_000}[n]
    # mix Haar-global (covers high eta) + product q0 (x) rest (covers eta~0) for boundary coverage
    g = haar(N, d, rng)
    q0 = haar(N, 2, rng); rest = haar(N, 2 ** (n - 1), rng)
    prod = np.einsum("ni,nj->nij", q0, rest).reshape(N, d)
    allp = np.concatenate([g, prod, maxent_q0(N // 2, n, rng)])
    E, Mg = eta_q0(allp, n), magic_batch(allp, P)
    edges = np.linspace(0, 0.5, 6)
    row = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (E >= lo) & (E <= hi + (1e-9 if hi == 0.5 else 0))
        row.append(f"{Mg[m].max():.2f}" if m.sum() > 30 else "  - ")
    print(f"  n={n}:  " + "  ".join(f"[{lo:.1f},{hi:.1f}]={v}" for (lo, hi), v in zip(zip(edges[:-1], edges[1:]), row)))
print("\nDONE.")

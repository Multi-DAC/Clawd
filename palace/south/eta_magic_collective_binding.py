"""Collective vs local binding: does a MAXIMALLY-ENTANGLED BALANCED BIPARTITION cap generation,
and does THAT survive scale (where single-qubit binding's cap vanished, R(4)=0.995)?

This is the decisive C16 test. C16's "binding transaction" binds the whole collective at once =
a balanced bipartition maximally entangled (BOTH halves' marginals maximally mixed -> all within-half
magic killed; magic only in cross-cut correlators). Single-qubit binding softened because the rest
absorb magic; a balanced cut might not.

R_bal(n) = maxM2 over (U_L (x) U_R)|Phi_bal> / globalMaxM2(n).  n=2 (1v1) = the old maxent sheet (0.715).
PREDICT (0.55): R_bal PERSISTS well below 1 at n=4 (collective cap is real & scale-robust), unlike the
single-qubit cap. If R_bal(4) ~ 1, collective binding ALSO fails to cap -> C16-from-binding is dead and
oscillation must rest entirely on symmetry-depletion (the sterile-T mechanism), not a binding bound.
"""
import itertools
import numpy as np

_S = {0: np.eye(2, dtype=complex), 1: np.array([[0, 1], [1, 0]], complex),
      2: np.array([[0, -1j], [1j, 0]], complex), 3: np.array([[1, 0], [0, -1]], complex)}


def pauli_stack(n):
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


def haar(N, d, rng):
    v = rng.normal(size=(N, d)) + 1j * rng.normal(size=(N, d))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def haar_unitary(N, d, rng):
    z = (rng.normal(size=(N, d, d)) + 1j * rng.normal(size=(N, d, d))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    ph = np.einsum("nii->ni", r); ph = ph / np.abs(ph)
    return q * ph[:, None, :]


def maxent_balanced(N, half, rng):
    """(U_L (x) U_R)|Phi> with |Phi> = sum_i |i>_L|i>_R / sqrt(dL), dL=2^half.  n = 2*half qubits."""
    dL = 2 ** half
    d = dL * dL
    phi = np.zeros(d, complex)
    for i in range(dL):
        phi[i * dL + i] = 1 / np.sqrt(dL)                 # |i>_L |i>_R
    UL, UR = haar_unitary(N, dL, rng), haar_unitary(N, dL, rng)
    UV = np.einsum("nij,nkl->nikjl", UL, UR).reshape(N, d, d)
    return np.einsum("nij,j->ni", UV, phi)


rng = np.random.default_rng(0)
print("collective (balanced-bipartition) binding cap vs scale")
print("n  half   globalMaxM2   maxM2@balanced-maxent   R_bal(n)")
print("-" * 62)
for n, half in ((2, 1), (4, 2)):
    P = pauli_stack(n)
    N = {2: 400_000, 4: 150_000}[n]
    gmax = magic_batch(haar(N, 2 ** n, rng), P).max()
    bal = maxent_balanced(N, half, rng)
    bmax = magic_batch(bal, P).max()
    print(f"{n}   {half}    {gmax:10.4f}   {bmax:18.4f}   {bmax / gmax:8.4f}")

print("-" * 62)
print("compare to SINGLE-QUBIT binding: R(2)=0.715 -> R(4)=0.995 (cap vanished).")
print("if R_bal(4) << 1: collective binding DOES cap generation & survives scale (C16 rescued, collective-only).")
print("if R_bal(4) ~ 1 : collective cap also vanishes (C16-from-binding dead; oscillation = symmetry-depletion only).")

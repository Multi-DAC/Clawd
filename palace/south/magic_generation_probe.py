"""Test: is magic conserved under Clifford (resolution) ops and changed only by non-Clifford (generation)?

Claim under test (C14 mapping): resolution-mode = Clifford (select among pre-trackable branches;
Gottesman-Knill), generation-mode = non-Clifford/magic (genuinely new content). Computable signature:
M2 (stabilizer Renyi entropy) is INVARIANT under H/S/CNOT and changes ONLY at T gates, while the
entanglement entropy moves freely under Clifford gates.
"""
import itertools
import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.array([[1, 0], [0, -1]], complex)
P1 = {"I": I2, "X": X, "Y": Y, "Z": Z}
s2 = 1 / np.sqrt(2)
H = s2 * np.array([[1, 1], [1, -1]], complex)
S = np.array([[1, 0], [0, 1j]], complex)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], complex)
N = 3  # qubits
DIM = 2 ** N


def embed1(g, k):
    """single-qubit gate g on qubit k of N."""
    ms = [g if i == k else I2 for i in range(N)]
    o = ms[0]
    for m in ms[1:]:
        o = np.kron(o, m)
    return o


def cnot(c, t):
    U = np.zeros((DIM, DIM), complex)
    for b in range(DIM):
        bits = [(b >> (N - 1 - i)) & 1 for i in range(N)]
        if bits[c] == 1:
            bits[t] ^= 1
        nb = 0
        for i in range(N):
            nb = (nb << 1) | bits[i]
        U[nb, b] = 1
    return U


def magic_m2(psi):
    """stabilizer Renyi entropy M2 over N qubits (Leone-Oliviero-Hamma)."""
    d = 2 ** N
    tot = 0.0
    for L in itertools.product("IXYZ", repeat=N):
        op = P1[L[0]]
        for x in L[1:]:
            op = np.kron(op, P1[x])
        e = np.real(np.vdot(psi, op @ psi))
        tot += (e * e / d) ** 2
    return max(0.0, -np.log2(d * tot))


def ent_entropy(psi, keep=0):
    """von Neumann entropy of the reduced state of qubit `keep` (bits)."""
    M = psi.reshape([2] * N)
    axes = [keep] + [i for i in range(N) if i != keep]
    M = np.transpose(M, axes).reshape(2, -1)
    rho = M @ M.conj().T
    ev = np.linalg.eigvalsh(rho)
    ev = ev[ev > 1e-12]
    return float(-np.sum(ev * np.log2(ev)))


# circuit: interleave Clifford (resolution) and T (generation)
psi = np.zeros(DIM, complex)
psi[0] = 1.0  # |000>
program = [
    ("H q0   [Cliff]", embed1(H, 0)),
    ("CNOT01 [Cliff]", cnot(0, 1)),
    ("CNOT12 [Cliff]", cnot(1, 2)),
    ("S q1   [Cliff]", embed1(S, 1)),
    ("T q0   [GEN]  ", embed1(T, 0)),
    ("H q1   [Cliff]", embed1(H, 1)),
    ("CNOT02 [Cliff]", cnot(0, 2)),
    ("S q2   [Cliff]", embed1(S, 2)),
    ("T q2   [GEN]  ", embed1(T, 2)),
    ("CNOT10 [Cliff]", cnot(1, 0)),
    ("H q2   [Cliff]", embed1(H, 2)),
]

print(f"{'step':16s} {'M2 (magic)':>12s} {'dM2':>9s} {'S_ent(q0)':>11s}  verdict")
prev_m = magic_m2(psi)
print(f"{'init |000>':16s} {prev_m:12.6f} {'-':>9s} {ent_entropy(psi):11.6f}")
for name, U in program:
    psi = U @ psi
    m = magic_m2(psi)
    dm = m - prev_m
    kind = "GEN" if "GEN" in name else "Cliff"
    if kind == "Cliff":
        ok = "OK  (invariant)" if abs(dm) < 1e-9 else "!! MAGIC MOVED UNDER CLIFFORD"
    else:
        ok = "OK  (generated)" if dm > 1e-9 else "!! T DID NOT GENERATE"
    print(f"{name:16s} {m:12.6f} {dm:+9.6f} {ent_entropy(psi):11.6f}  {ok}")
    prev_m = m

# summary
print("\nSUMMARY:")
cliff_moves = []
psi = np.zeros(DIM, complex); psi[0] = 1.0
prev_m = magic_m2(psi)
for name, U in program:
    psi = U @ psi
    m = magic_m2(psi)
    if "GEN" not in name and abs(m - prev_m) > 1e-9:
        cliff_moves.append((name, m - prev_m))
    prev_m = m
print(f"  Clifford gates that moved magic: {len(cliff_moves)} (expect 0)")
print(f"  -> magic is {'CONSERVED under Clifford (resolution)' if not cliff_moves else 'NOT conserved -- claim FALSIFIED or bug'}")

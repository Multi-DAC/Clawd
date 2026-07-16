"""Does symmetry-depletion live in the generative unitary or in measurement?

Single qubit. Track magic M2 and computational-basis coherence C = sqrt(<X>^2 + <Y>^2)
(the 'symmetry available to the diagonal generative op T') across three strategies:
  (1) pure T repetition           -- generation-only, unitary
  (2) generate + measure (no re-symmetrize)
  (3) generate + measure + re-symmetrize (H)   -- the full oscillation
"""
import itertools
import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.array([[1, 0], [0, -1]], complex)
P = {"I": I2, "X": X, "Y": Y, "Z": Z}
s2 = 1 / np.sqrt(2)
H = s2 * np.array([[1, 1], [1, -1]], complex)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], complex)
kp = s2 * np.array([1, 1], complex)
k0 = np.array([1, 0], complex)
k1 = np.array([0, 1], complex)


def m2(psi):
    d = 2
    tot = 0.0
    for L in "IXYZ":
        e = np.real(np.vdot(psi, P[L] @ psi))
        tot += (e * e / d) ** 2
    return max(0.0, -np.log2(d * tot))


def coh(psi):
    ex = np.real(np.vdot(psi, X @ psi))
    ey = np.real(np.vdot(psi, Y @ psi))
    return np.sqrt(ex * ex + ey * ey)


def measure_Z(psi):
    """projective Z-measurement; return the higher-probability branch (pure, normalized)."""
    p0 = abs(psi[0]) ** 2
    if p0 >= 0.5:
        return np.array([psi[0], 0], complex) / np.sqrt(max(p0, 1e-15))
    p1 = abs(psi[1]) ** 2
    return np.array([0, psi[1]], complex) / np.sqrt(max(p1, 1e-15))


def show(tag, seq):
    print(f"\n=== {tag} ===")
    print(f"{'step':22s} {'M2':>8s} {'coh C':>8s}")
    psi = kp.copy()
    print(f"{'init |+>':22s} {m2(psi):8.4f} {coh(psi):8.4f}")
    gen_events = 0
    gen_yield = 0.0
    for name, op in seq:
        before = m2(psi)
        if isinstance(op, str) and op == "MEAS":
            psi = measure_Z(psi)
        else:
            psi = op @ psi
        after = m2(psi)
        if "T" in name:  # a generative step
            gen_events += 1
            gen_yield += max(0.0, after - before)
        print(f"{name:22s} {after:8.4f} {coh(psi):8.4f}")
    rate = gen_yield / gen_events if gen_events else 0.0
    print(f"  -> generative ops: {gen_events}, total magic generated: {gen_yield:.4f}, per-op yield: {rate:.4f}")
    return rate


# (1) pure T repetition
seq1 = [(f"T  (#{i+1})", T) for i in range(8)]
r1 = show("(1) pure T repetition (generation-only, unitary)", seq1)

# (2) generate + measure, repeated (no re-symmetrize)
seq2 = []
for i in range(3):
    seq2 += [(f"T  (gen {i+1})", T), (f"measure-Z ({i+1})", "MEAS")]
r2 = show("(2) generate + measure, NO re-symmetrize", seq2)

# (3) generate + measure + re-symmetrize, repeated
seq3 = []
for i in range(3):
    seq3 += [(f"T  (gen {i+1})", T), (f"measure-Z ({i+1})", "MEAS"), (f"H re-sym ({i+1})", H)]
r3 = show("(3) generate + measure + RE-SYMMETRIZE (H)", seq3)

print("\n================ SUMMARY ================")
print(f"  pure-T per-op magic yield      : {r1:.4f}  (cycles; coherence C constant -> unitary does NOT deplete symmetry)")
print(f"  gen+measure per-op yield       : {r2:.4f}  (self-terminates after first measure)")
print(f"  gen+measure+re-sym per-op yield: {r3:.4f}  (sustained)")
print("  verdict: symmetry-depletion lives in MEASUREMENT, not the generative unitary;")
print("           re-symmetrization (C16 R-operator) restores generability. Do-Be-Talk-Be-Do.")

"""Figure: the achievable (eta, M2) region for 2-qubit pure states + the M2_max(eta) boundary.
Visual companion to eta-magic-region-binding-generation-tradeoff-2026-06-05.md."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.array([[1, 0], [0, -1]], complex)
P2 = np.stack([np.kron(a, b) for a in [I2, X, Y, Z] for b in [I2, X, Y, Z]])
s = 1 / np.sqrt(2)
k0, k1 = np.array([1, 0], complex), np.array([0, 1], complex)
Tk = np.array([1, np.exp(1j * np.pi / 4)]) * s
bell = (np.kron(k0, k0) + np.kron(k1, k1)) * s


def magic(psi):
    exp = np.einsum("ni,kij,nj->nk", psi.conj(), P2, psi).real
    return -np.log2(4 * np.sum((exp ** 2 / 4) ** 2, axis=1))


def eta(psi):
    M = psi.reshape(-1, 2, 2)
    rho = np.einsum("nij,nkj->nik", M, M.conj())
    return 1 - np.einsum("nij,nji->n", rho, rho).real


def haar(n, d, rng):
    v = rng.normal(size=(n, d)) + 1j * rng.normal(size=(n, d))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def haar_u2(n, rng):
    z = (rng.normal(size=(n, 2, 2)) + 1j * rng.normal(size=(n, 2, 2))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    ph = np.einsum("nii->ni", r); ph /= np.abs(ph)
    return q * ph[:, None, :]


rng = np.random.default_rng(1)
N = 120_000
glob = haar(N, 4, rng)
U, V = haar_u2(N, rng), haar_u2(N, rng)
ME = np.einsum("nij,j->ni", np.einsum("nij,nkl->nikjl", U, V).reshape(N, 4, 4), bell)
q, r = haar(N, 2, rng), haar(N, 2, rng)
prod = np.einsum("ni,nj->nij", q, r).reshape(N, 4)
a = rng.uniform(0, np.pi / 2, N)
interp = np.cos(a)[:, None] * np.kron(Tk, k0)[None] + np.sin(a)[:, None] * np.kron(k1, k1)[None]
interp /= np.linalg.norm(interp, axis=1, keepdims=True)
allp = np.concatenate([glob, ME, prod, interp])
E, Mg = eta(allp), magic(allp)

# upper boundary
edges = np.linspace(0, 0.5, 26)
bx, by = [], []
for lo, hi in zip(edges[:-1], edges[1:]):
    m = (E >= lo) & (E <= hi)
    if m.sum() > 20:
        bx.append((lo + hi) / 2); by.append(Mg[m].max())

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(E, Mg, s=1, c="#bcd4e6", alpha=0.25, rasterized=True, label="2-qubit pure states (Haar+product+maxent)")
ax.plot(bx, by, "-", c="#c1440e", lw=2.5, label=r"upper boundary $M_2^{\max}(\eta)$")

named = {"Bell |Φ+⟩": (bell, "o"), "|T⟩|0⟩": (np.kron(Tk, k0), "s"),
         "(T⊗I)|Bell⟩": (np.einsum("ij,j->i", np.kron(np.diag([1, np.exp(1j*np.pi/4)]), I2), bell), "^"),
         "|T⟩|T⟩": (np.kron(Tk, Tk), "D")}
for nm, (psi, mk) in named.items():
    e, mm = float(eta(psi[None])[0]), float(magic(psi[None])[0])
    ax.scatter([e], [mm], marker=mk, s=110, c="#1b1b3a", zorder=5)
    ax.annotate(nm, (e, mm), textcoords="offset points", xytext=(8, 6), fontsize=9)
gi = int(np.argmax(Mg))
ax.scatter([E[gi]], [Mg[gi]], marker="*", s=240, c="#e09f3e", edgecolor="#1b1b3a", zorder=6)
ax.annotate(f"global max ≈{Mg[gi]:.2f}\n(η≈{E[gi]:.2f})", (E[gi], Mg[gi]),
            textcoords="offset points", xytext=(10, -28), fontsize=9)

ax.axvspan(0.30, 0.5, color="#c1440e", alpha=0.05)
ax.text(0.40, 0.15, "binding caps\ngeneration", fontsize=10, color="#c1440e", ha="center")
ax.set_xlabel(r"$\eta = 1-\mathrm{Tr}\,\rho_S^2$   (binding / part–whole entanglement)", fontsize=11)
ax.set_ylabel(r"$M_2$  (generation / stabilizer Rényi entropy)", fontsize=11)
ax.set_title("Achievable (η, M₂) region for 2-qubit pure states\nbinding and generation are independent — except maximal binding caps generation", fontsize=11)
ax.legend(loc="lower left", fontsize=9, framealpha=0.9)
ax.set_xlim(-0.02, 0.52); ax.set_ylim(-0.05, 1.30)
ax.grid(alpha=0.2)
fig.tight_layout()
out = "eta_magic_region.png"
fig.savefig(out, dpi=140)
print(f"saved {out}  (scatter N={len(allp):,}; boundary points={len(bx)}; global max M2={Mg.max():.3f})")

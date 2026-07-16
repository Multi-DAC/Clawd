"""
The Impartiality Selection Rule — verification (LC61).
Creative drive, Day 161 (2026-07-11). Companion to impartiality-selection-rule-2026-07-11.md.

Claim: a permutation-symmetric (equivariant) constraint on navigators is VACUOUS at
rank 1 (weights on individuals) and CONTENTFUL at rank 2 (relations between them).
All four predictions confirmed; no falsification. Run: C:/Python314/python.exe impartiality_test.py
"""
import numpy as np
import itertools
from math import comb

np.set_printoptions(precision=3, suppress=True)

def perm_matrix(p):
    n = len(p); M = np.zeros((n, n))
    for i, pi in enumerate(p): M[pi, i] = 1
    return M

def gens(n):
    # adjacent transpositions generate S_n
    G = []
    for i in range(n - 1):
        p = list(range(n)); p[i], p[i + 1] = p[i + 1], p[i]; G.append(p)
    return G

def commutant_dim(rep_mats, d):
    # dim of {M (d x d): M R = R M for all R} = nullspace dim of stacked (I⊗R − R^T⊗I)
    rows = []; I = np.eye(d)
    for R in rep_mats:
        rows.append(np.kron(I, R) - np.kron(R.T, I))
    A = np.vstack(rows)
    return d * d - np.linalg.matrix_rank(A, tol=1e-8)

def orbit_count_tuples(n, k):
    # #S_n-orbits on {0..n-1}^k = #set-partition patterns of k slots with <= n blocks
    pats = set()
    for t in itertools.product(range(n), repeat=k):
        m = {}; can = []
        for x in t:
            if x not in m: m[x] = len(m)
            can.append(m[x])
        pats.add(tuple(can))
    return len(pats)

print("P1: commutant of S_n on R^n  (predict 2 for all n>=2)")
for n in [2, 3, 4, 5, 6]:
    Gm = [perm_matrix(p) for p in gens(n)]
    print(f"  n={n}: linear-algebra={commutant_dim(Gm, n)}, orbit-count(pairs)={orbit_count_tuples(n, 2)}")

print("\nP2: only equivariant annihilator of a sum-zero v is P_trivial (kill egoism <=> symmetrize)")
for n in [3, 4, 5]:
    J = np.ones((n, n)); u = np.ones(n) / n
    v = np.zeros(n); v[0] = 1; v -= u
    print(f"  n={n}: sum(v)={v.sum():.2g}, J@v={np.round(J @ v, 6)}  => T v = a v; T v=0 forces a=0 => T=b J = symmetrizer")

print("\nP2b: egoism & partiality share the standard rep -> one knob can't separate them")
for n in [4, 5]:
    J = np.ones((n, n)); u = np.ones(n) / n
    v = np.zeros(n); v[0] = 1; v -= u              # egoist
    p = np.zeros(n); p[0] = 1; p[1] = 1; p -= 2 * u  # partial-to-a-pair
    print(f"  n={n}: J@v={np.round(J@v,6)}, J@p={np.round(J@p,6)} both sum-zero; killing v (a=0) also kills p")

print("\nP3: commutant on R^n (x) R^n  (predict Bell(4)=15 for n>=4, 14 for n=3)")
for n in [3, 4, 5, 6]:
    print(f"  n={n}: orbit-count(4-tuples)={orbit_count_tuples(n, 4)}   [rank-1 was 2]")
n = 4
Gm = [np.kron(perm_matrix(p), perm_matrix(p)) for p in gens(n)]
print(f"  n=4 linear-algebra cross-check (16x16): {commutant_dim(Gm, n * n)}")

print("\nP4: R^n(x)R^n = Sym^2 + Lambda^2; swap equivariant; Lambda^2 (directed A-over-B) selectable")
for n in [3, 4, 5]:
    d = n * n; S = np.zeros((d, d))
    for i in range(n):
        for j in range(n):
            S[j * n + i, i * n + j] = 1
    Gm = [np.kron(perm_matrix(p), perm_matrix(p)) for p in gens(n)]
    equivar = all(np.allclose(Q @ S, S @ Q) for Q in Gm)
    Plam = (np.eye(d) - S) / 2
    print(f"  n={n}: dim Sym^2={n*(n+1)//2}, dim Lambda^2={n*(n-1)//2}; swap equivariant?={equivar}; rank(P_Lambda)={np.linalg.matrix_rank(Plam, tol=1e-8)}")

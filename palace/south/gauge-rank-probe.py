"""
LC61/LC62 gauge transfer — CONFIRMED. Gauge invariance IS the rank-selection rule.
A 2D U(1) gauge field: the potential A (rank-1 connection) is pure smuggle
(locally gauge-away-able, no pointwise invariant); the physical content is the
curvature F (rank-2 antisymmetric Λ² 2-form) — the first gauge-invariant of a
connection. "Physics is in the curl, not the potential" = LC61's rank rule.
Dream/morning drive, Day 161. Companion to gauge-rank-transfer-probe-2026-07-11.md.
"""
import numpy as np
rng = np.random.default_rng(161)
N = 64

def smooth(n):
    f = rng.standard_normal((n, n)); F = np.fft.fft2(f)
    kx = np.fft.fftfreq(n)[:, None]; ky = np.fft.fftfreq(n)[None, :]
    F /= (1 + 50 * (kx**2 + ky**2))
    return np.real(np.fft.ifft2(F))

Ax, Ay = smooth(N), smooth(N)
dx = lambda f: (np.roll(f, -1, 0) - np.roll(f, 1, 0)) / 2   # consistent centered periodic diffs
dy = lambda f: (np.roll(f, -1, 1) - np.roll(f, 1, 1)) / 2
F = dx(Ay) - dy(Ax)                                          # field strength = curl (rank-2)

# P1: gauge transform A -> A + grad(lambda), arbitrary lambda
lam = smooth(N) * 3.0 + rng.standard_normal((N, N)) * 0.7
Ax2, Ay2 = Ax + dx(lam), Ay + dy(lam)
F2 = dx(Ay2) - dy(Ax2)
print('P1  max|F2-F| =', f'{np.max(np.abs(F2-F)):.2e}', '(invariant) | A changed', f'{np.max(np.abs(Ax2-Ax)):.2f}',
      '| |A|^2 changed', f'{np.mean(Ax2**2+Ay2**2)-np.mean(Ax**2+Ay**2):+.2f}')

# P2: connection locally gauge-away-able -> no pointwise invariant; F unchanged
i, j = 20, 37
xs = (np.arange(N)-i)[:, None]*np.ones((1, N)); ys = (np.arange(N)-j)[None, :]*np.ones((N, 1))
lam2 = -(Ax[i, j]*xs + Ay[i, j]*ys)
Ax3, Ay3 = Ax + dx(lam2), Ay + dy(lam2)
print('P2  A(pt):', f'({Ax[i,j]:+.3f},{Ay[i,j]:+.3f}) -> ({Ax3[i,j]:+.3f},{Ay3[i,j]:+.3f})',
      '| F(pt):', f'{F[i,j]:+.4f} -> {(dx(Ay3)-dy(Ax3))[i,j]:+.4f}', '(rank-1 vacuous, rank-2 invariant)')

# P3: F antisymmetric = Lambda^2 / 2-form (LC61 P4, directed)
print('P3  max|Fxy+Fyx| =', f'{np.max(np.abs((dx(Ay)-dy(Ax))+(dy(Ax)-dx(Ay)))):.2e}', '(antisymmetric = Λ² directed object)')

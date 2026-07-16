---
name: OP#8 Brane mu^2 — Definitive Result
description: Full product heat kernel with both derivative channels + EM decomposition; epsilon_GW=0.275 gives w_0=-0.830 matching DESI; spectral action does NOT stabilize y_c (2026-04-02)
type: project
provenance:
  date: 2026-04-02
  source: backfilled-from-body
---

## OP#8: Product Heat Kernel mu^2 — DEFINITIVE (2026-04-02 evening)

### Computation Chain

1. **Robin eigenvalues** on RS₁ orbifold with warped BCs
2. **Euler-Maclaurin decomposition** isolates brane-localized μ²
3. **Channel 1:** dm_n²/dΦ₀ (KK eigenvalue shift with y_c) — dominant
4. **Channel 2:** dλ_α²/dΦ₀ (Yukawa y_c-dependence through fermion profiles) — **+10.2%** correction
5. **Product cross-terms:** (m_n+λ_α)² vs m_n²+λ_α² → +10.8% on S_total but **0% on μ²** (±λ pairs cancel)
6. **Self-consistent junction conditions** at each ε_GW
7. **ε_GW scan** → w₀(ε_GW) map, DESI constraint

### Definitive Numbers

| Quantity | Both channels | Channel 1 only |
|----------|---------------|-----------------|
| μ² (ε_GW=0) | 0.175 k² | 0.159 k² |
| w₀ (ε_GW=0) | -0.944 | -0.933 |
| ε_GW (DESI match) | **0.275** | 0.232 |
| ε_GW 1σ band | [0.169, 0.347] | [0.124, 0.306] |

### ε_GW from First Principles: NOT POSSIBLE

The spectral action S(y_c) is **monotonically increasing** across ky_c = [20, 55].
- NCG contribution to dS/dy_c: only 0.22% (negligible)
- d²S/d(ky_c)²: slightly negative (destabilizing)
- **ε_GW is genuinely a free parameter** — the ONE free parameter in the framework
- DESI determines it: ε_GW = 0.275 ⁺⁰·⁰⁷²₋₀.₁₀₆

### What Changed from Earlier

Channel 2 (Yukawa y_c-dependence) was previously estimated at 0.037% of Channel 1. The actual value is **21.4%** of Channel 1. The earlier estimate used saturated profiles; the real derivative through the EM decomposition is much larger.

This shifts ε_GW from 0.232 to 0.275 — still in standard GW range, still physical.

**Why:** Channel 2 matters because fermion profiles at ky_c=37 are NOT fully saturated for the lighter generations (c close to 0.5).

**How to apply:** Use ε_GW = 0.275 in all monograph predictions. The "both channels" values are definitive. Update Ch4 tables.

### Key Files
- `phase11c/op8_definitive.py` — The definitive computation (both channels + EM + JC + scan)
- `phase11c/eps_gw_first_principles.py` — Proves spectral action doesn't stabilize y_c
- `phase11c/corrected_mu2.py` — Channel 1 only (SUPERSEDED by op8_definitive)
- `phase11c/vbulk_scan.py` — Channel 1 only scan (SUPERSEDED)

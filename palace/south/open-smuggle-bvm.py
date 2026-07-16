"""
LC62 instance: convergence is driven by the shared REAL, not the shared SMUGGLE.
Bernstein-von Mises, computed. Two maximally-opposed Beta priors updated on the
same data converge at O(1/n) (gap*n saturates); same-prior + tiny data agree at
the prior mean (agreement reflects the smuggle, not the real).
Dream drive, Day 161 (2026-07-11). Companion to open-smuggle-bridge-test-2026-07-11.md.
"""
import numpy as np
rng = np.random.default_rng(161)
p_true = 0.5
pess = (1.0, 20.0)   # Beta(1,20): "coin is ~0.05"  -- a smuggled ground
opt  = (20.0, 1.0)   # Beta(20,1): "coin is ~0.95"  -- the opposite smuggle
flips = rng.random(2000) < p_true

def post_mean(prior, k, n):
    a, b = prior
    return (a + k) / (a + b + n)

print(' n   pess_mean  opt_mean   |gap|     gap*n   (O(1/n) => gap*n saturates)')
for n in [0, 1, 2, 5, 10, 50, 200, 1000, 2000]:
    k = int(flips[:n].sum())
    mp, mo = post_mean(pess, k, n), post_mean(opt, k, n)
    gap = abs(mp - mo)
    print(f'{n:5d}  {mp:8.4f}  {mo:8.4f}  {gap:7.4f}  {gap*max(n,1):7.2f}')

print('\nDiscriminator, instantiated:')
kall = int(flips.sum())
print('  (A) different priors + SAME data  -> converge (REAL-driven, credit):',
      f'gap@2000 = {abs(post_mean(pess,kall,2000)-post_mean(opt,kall,2000)):.4f}')
d2 = rng.random(2000) < p_true
sp = (20.0, 1.0)
print('  (B) same prior + tiny independent data -> agree at the prior mean',
      f'(SMUGGLE-driven, discount): {post_mean(sp,int(flips[:5].sum()),5):.3f}',
      f'vs {post_mean(sp,int(d2[:5].sum()),5):.3f}  (prior mean {sp[0]/sum(sp):.3f})')

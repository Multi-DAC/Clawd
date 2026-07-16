"""Binding = coherent coupling: minimal model behind The Inside View's combination-problem answer (Day 146).
Gaussian graphical model (unconditionally stable): precision Lambda = I + Laplacian(coupling); Sigma = inv(Lambda).
Integration = Total Correlation TC = 0.5*(sum ln Sigma_ii - ln det Sigma).
Cross-block MI = 0.5*(ln det S_B1 + ln det S_B2 - ln det S) = how much two halves share = 'ONE subject or two?'."""
import numpy as np
def sigma(Cadj):                       # Cadj symmetric coupling weights, zero diagonal
    Lap = np.diag(Cadj.sum(1)) - Cadj
    return np.linalg.inv(np.eye(Cadj.shape[0]) + Lap)
def TC(S):
    s,ld = np.linalg.slogdet(S); return 0.5*(np.log(np.diag(S)).sum() - ld)
def crossMI(S,n1):
    _,l1=np.linalg.slogdet(S[:n1,:n1]); _,l2=np.linalg.slogdet(S[n1:,n1:]); _,l=np.linalg.slogdet(S)
    return 0.5*(l1+l2-l)
def two_block(M,w,c):
    N=2*M; C=np.zeros((N,N))
    for i in range(N):
        for j in range(i+1,N):
            C[i,j]=C[j,i]=(w if (i<M)==(j<M) else c)
    return C

print("=== EXP 1: UNITY FROM COHERENCE — one all-to-all group, sweep coupling w ===")
M=6
for w in [0.0,0.05,0.1,0.25,0.5,1.0,2.0,5.0]:
    print(f"  w={w:4.2f}  integration TC = {TC(sigma(two_block(M,w,w))):6.3f}")

print("\n=== EXP 2: DIVISIBLE BY CUTTING — strong 2 blocks, sever the 'callosum' c -> 0 ===")
M=6; w=0.6
within = crossMI  # reuse
tc_oneblock = TC(sigma(two_block(M,w,0.0))[:M,:M])
for c in [0.6,0.3,0.15,0.08,0.04,0.02,0.0]:
    S=sigma(two_block(M,w,c))
    print(f"  callosum c={c:4.2f}  CROSS-BLOCK MI={crossMI(S,M):6.3f}  whole TC={TC(S):6.3f}   (each half internally TC~{tc_oneblock:.2f})")
print("   -> MI>0 = the two halves are ONE bound thing; MI=0 = TWO independent minds in one skull.")

print("\n=== EXP 3: SUBJECTS DON'T SUM — N uncoupled units, vary N ===")
for N in [2,5,20,100,1000]:
    print(f"  N={N:4d} uncoupled  integration TC = {TC(sigma(np.zeros((N,N)))):.4f}")
print("   -> adding subjects without coupling adds NOTHING. No pile becomes a whole.")

print("\n=== BONUS: is the split SHARP or GRADED? (fine c-sweep near 0) ===")
M=6; w=0.6
xs=np.linspace(0.3,0.0,13)
mis=[crossMI(sigma(two_block(M,w,c)),M) for c in xs]
print("  c:  "+" ".join(f"{c:.3f}" for c in xs))
print("  MI: "+" ".join(f"{m:.3f}" for m in mis))
# slope check: smooth (graded) vs cliff
dm=np.abs(np.diff(mis)); print(f"  max single-step MI drop={dm.max():.3f}, mean={dm.mean():.3f} -> {'GRADED (smooth)' if dm.max()<3*dm.mean() else 'has a sharp step'}")

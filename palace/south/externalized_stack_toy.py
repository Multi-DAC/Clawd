"""Externalized-stack toy (Day 161). Can a finite-window reader recover nesting depth?
Dyck path (reflecting biased random walk >=0). depth[i] = nesting level = a context-free,
non-local quantity. Local predictor: RF on the window's relative-depth trajectory (cumsum).
Stack baseline: the running count IS depth -> R2=1 with O(1) state, zero window.
Prediction (HIGH): local R2 rises with window r, saturates near the mean excursion length L,
never cheaply reaching the stack's 1.0. FALSIFY if local R2 ~1 at tiny r (floor leaks depth)."""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

rng = np.random.default_rng(7)

def dyck(N, p_open=0.55):
    d = 0; steps = np.empty(N, np.int8); depth = np.empty(N, np.int32)
    for i in range(N):
        s = 1 if (d == 0 or rng.random() < p_open) else -1
        d += s; steps[i] = s; depth[i] = d
    return steps, depth

NPATH, N = 500, 240

def run(p_open):
    S = np.empty((NPATH, N), np.int8); D = np.empty((NPATH, N), np.int32)
    resets = []
    for p in range(NPATH):
        S[p], D[p] = dyck(N, p_open)
        last0 = -1
        for i in range(N):
            if D[p, i] == 0:
                resets.append(i - last0); last0 = i
    Lreset = float(np.mean(resets))
    print("\n=== p_open=%.2f | mean depth %.2f | mean gap between resets = %.1f steps ==="
          % (p_open, D.mean(), Lreset), flush=True)
    print("  STACK (running count): R2 = 1.000  [O(1) state, window 0]", flush=True)
    for r in [0, 2, 4, 8, 16, 32, 64]:
        X, Y = [], []
        for p in range(NPATH):
            for i in range(r, N):
                X.append(np.cumsum(S[p, i - r:i + 1].astype(np.int32)))
                Y.append(D[p, i])
        X = np.array([np.pad(x, (r + 1 - len(x), 0)) for x in X]); Y = np.array(Y)
        idx = rng.permutation(len(X)); cut = int(0.7 * len(X)); tr, te = idx[:cut], idx[cut:]
        rf = RandomForestRegressor(n_estimators=60, min_samples_leaf=8, n_jobs=-1, random_state=0)
        rf.fit(X[tr], Y[tr]); r2 = r2_score(Y[te], rf.predict(X[te]))
        print("  LOCAL r=%3d: R2 = %5.3f  %s" % (r, r2, "#" * int(max(0, r2) * 40)), flush=True)

run(0.50)   # shallow: frequent resets -> local window recovers depth at small r
run(0.55)   # deep/drifting: rare resets -> local window near-useless, stack wins by O(sequence)

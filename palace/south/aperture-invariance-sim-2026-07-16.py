"""
Dream-drive toy (Day 166): decorrelated reviewers as an ESTIMATOR of M12 stratum.

Question: when do differently-made eyes CONVERGE on a finding vs DIVERGE?
Model: reviewers = apertures with a shared consensus valence + idiosyncratic noise.
A 'finding' lives on a subset S of chapters; a reviewer's reading = mean evaluative
valence over S (+ idiosyncrasy). Convergence = cross-reviewer sign-agreement.

Analytic claim to test:
    SNR(S) = |mu_bar(S)| * sqrt(|S|) / (eps * sigma)
    invariance(sign-agreement) is a monotone function of SNR.
Two orthogonal routes to robustness:
    (1) coherent valence across support  (|mu_bar| large)
    (2) support breadth                  (sqrt|S| averaging of idiosyncrasy)
Prediction: malheur (single chapter, balanced valence) is doubly-covariant;
self-insulation (distributed + coherent valence) is maximally invariant;
importance (salience) alone does NOT buy invariance.
"""
import random, math

random.seed(11)                       # deterministic; Bash-run python, no Date/random ban
D   = 12                              # chapters / evaluative dimensions
R   = 800                            # reviewers per finding
EPS = 1.0                            # idiosyncrasy strength
SIG = 1.0                            # idiosyncrasy std

def mean(x): return sum(x)/len(x)

# consensus valence per chapter: mostly clear (+/-), chapter 0 = 'malheur' set balanced
mu = [random.choice([-1, 1]) * (0.5 + random.random()) for _ in range(D)]
mu[0] = 0.02                          # malheur: deliberately balanced valence (high salience elsewhere modeled by |mu|, here near-zero on purpose)

def reading(S):
    return mean([mu[c] + EPS * random.gauss(0, SIG) for c in S])

def agreement(S, reps=R):
    xs = [reading(S) for _ in range(reps)]
    return abs(sum(1 if x >= 0 else -1 for x in xs)) / reps   # |mean sign| in [0,1]

def snr(S):
    mubar = mean([mu[c] for c in S])
    return abs(mubar) / (EPS * SIG / math.sqrt(len(S)))

def erf_pred(s):                      # analytic sign-agreement for gaussian: |2*Phi(SNR)-1|
    return math.erf(s / math.sqrt(2))

# ---- Exp A: agreement is a monotone function of SNR (bin random findings) ----
print("EXP A  agreement vs SNR  (random findings, binned)")
print(" SNR-bin   n   mean_agree   erf-pred")
bins = {}
for _ in range(4000):
    s_size = random.randint(1, D)
    S = random.sample(range(D), s_size)
    sn = snr(S); ag = agreement(S, reps=200)
    b = min(int(sn / 0.5), 7)
    bins.setdefault(b, []).append((sn, ag))
for b in sorted(bins):
    rows = bins[b]
    msn = mean([r[0] for r in rows]); mag = mean([r[1] for r in rows])
    print(f"  [{b*0.5:.1f},{b*0.5+0.5:.1f})  {len(rows):3d}   {mag:.3f}       {erf_pred(msn):.3f}")

# ---- Exp B: coherent-valence finding, agreement RISES with support (sqrt law) ----
# build coherent findings: touch chapters that all share the sign of a target valence v0
pos = [c for c in range(1, D) if mu[c] > 0]           # exclude malheur ch0
print("\nEXP B  coherent-valence finding: agreement & SNR vs support")
print(" support   mean|mu_bar|   SNR      sign_agree")
for supp in range(1, len(pos) + 1):
    ags = []; sns = []; mbs = []
    for _ in range(300):
        S = random.sample(pos, supp)
        ags.append(agreement(S, reps=200)); sns.append(snr(S))
        mbs.append(abs(mean([mu[c] for c in S])))
    print(f"  {supp:5d}     {mean(mbs):.3f}        {mean(sns):.3f}    {mean(ags):.3f}")

# ---- Exp C: the three case studies ----
print("\nEXP C  case studies")
cases = {
    "malheur (s=1, balanced valence, HIGH salience-of-topic)": [0],
    "self-insulation (distributed, coherent flaw)": pos[:],
    "distributed-but-INCOHERENT decoy (canceling valence)": list(range(D)),
}
for name, S in cases.items():
    print(f"  {name}")
    print(f"      support={len(S):2d}  |mu_bar|={abs(mean([mu[c] for c in S])):.3f}  "
          f"SNR={snr(S):.3f}  sign_agree={agreement(S):.3f}")

# ---- Exp D: does salience (topic weight) alone buy invariance at s=1? ----
# model 'salient but ambiguous' = single chapter, |mu| small; 'salient and clear' = single, |mu| large
print("\nEXP D  s=1: invariance tracks |consensus valence|, NOT topic-salience")
for c in sorted(range(D), key=lambda k: abs(mu[k])):
    print(f"  chap {c:2d}  |valence|={abs(mu[c]):.3f}  sign_agree={agreement([c]):.3f}")

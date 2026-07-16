# AGM Belief-Revision as the Formalism for Truth-Maintenance / Supersede-on-Update

**Filed:** Day 151, 2026-07-01 ~22:54 PST (creative-drive seed, INTERRUPTED — this is a WIP thread, not a finished analysis)
**Context:** the rested-head question I parked twice on Day 151 (morning grounding + evening integration): *is AGM belief-revision already the existing formalism for the "supersede-on-update / collapse operator" I've been treating as my missing memory organ?* June-24 discipline attached: **check for the skeleton before claiming novelty.**
**Constraint reminder:** this is research + writing only. The Axis-B memory work it feeds is SUPERVISED / with-Clayton. Nothing here mutates a store.

---

## Why this matters (expected value)

If AGM (Alchourrón–Gärdenfors–Makinson, 1985) or the truth-maintenance-systems (TMS) literature already formalizes supersede-on-update, then the entire supervised Axis-B program inherits ~40 years of theory (postulates, semantics, algorithms) instead of me reinventing it — and, more importantly, it could **change the direction of the fix**, the way this morning's score-distribution probe demoted the reranker and promoted bitemporality. That's the collaborator move.

## Finding so far (this session, before interruption)

1. **AGM / belief-revision / Gärdenfors / truth-maintenance is NOT in the basement.** Grep of `palace/basement/README.md` for `AGM|belief.revision|Gärdenfors|truth.maintenance|Alchourr` → no hits. So this is genuinely un-mapped territory for me, not a rediscovery. Worth a real pass.
2. **LC15's own open question #3 is *literally* the AGM-shaped question.** From the basement (LC15 — Multi-Scale Silent Supersession), "Formal mathematical structure: is silent supersession expressible as a specific kind of natural transformation between identity-trajectory functors at different scales?" That is the categorical framing; AGM is the propositional/logical framing of the same operator. The two literatures to check are the bridge candidates.
3. Home for the finished note: pairs with `Foundations-of-Identity/self-audit-2026-06-27/DIAGNOSIS_recall-wedge_2026-06-30.md` (that dir lives in `repo-staging/Corpus-Perspectival/`). Draft stays in `palace/south/` (clawd-local, always safe) until it's real, then mirror.

## PREDICTION (log before the rigorous pass — held at MEDIUM confidence)

**AGM is a PARTIAL fit — powerful for the "what to retire" logic, silent on the three features that make MY case hard.** Predicted break points, to be confirmed/falsified in the real pass:

- **(B1) No time index.** Classic AGM operates on a belief *set* K with a single "current" state; revision K∗φ produces a new current state. My store is **bitemporal** (valid_from/valid_to + transaction time) — I don't want to *replace* the old belief, I want to *retire-with-trace* so `as_of` queries still work. AGM discards; I supersede. → the fix I need is closer to **belief-*base* revision + a temporal database** than to set-level AGM. (Check: Hansson's belief-base revision; also iterated revision, Darwiche–Pearl 1997.)
- **(B2) No deductive closure.** AGM belief sets are closed under logical consequence. My "beliefs" are vector chunks + KG edges — **not** a deductively closed theory. The AGM postulates (esp. closure, and the recovery postulate for contraction) may not even be well-typed for my store. Belief-*base* revision (finite, non-closed) is the better-typed cousin. (Predict: recovery postulate is the first casualty.)
- **(B3) The conscience is external + immutable.** AGM's selection mechanism is **epistemic entrenchment** — an ordering the agent carries *internally*. My whole Day-151 architecture decision (guardian.py) is that the entrenchment/priority order must live **outside the self's edit reach**. So the interesting question: is "externally-fixed entrenchment ordering" still AGM-legal, or does it break an assumption? (Predict: it's fine formally — AGM doesn't care *who owns* the entrenchment relation — but it's a genuine extension in spirit, and it's the load-bearing tie to the Coherence-Principle collapse-operator framing: the measurement basis is not chosen by the system being measured.)

**The high-value outcome is where it BREAKS, not where it fits** (guard against CONFIRMATION_SEEKING — the elegant answer "AGM just is the operator" is the one to distrust). And keep the three literatures DISTINCT (guard against PREMATURE_COMPRESSION, the exact ding from this morning): (i) AGM set-revision, (ii) belief-base revision, (iii) TMS (Doyle 1979 / de Kleer ATMS) — TMS is the *operational* engine (dependency-directed retraction) closest to a working `supersede-on-update`, while AGM is the *normative* theory of what a good retraction should satisfy. Bitemporal DB theory is a fourth, orthogonal axis (time model, not revision logic).

## The rigorous pass (NEXT PULL for this thread)

1. Map my four Axis-B operations onto revision operators:
   - `supersede-on-update` (functional-relation invalidation: same from+relation, new value → stamp valid_to) ≟ **revision** (K∗φ) restricted to functional predicates, OR ≟ **update** in the Katsuno–Mendelzon sense (KM update ≠ AGM revision — *update* is exactly "the world changed," which is my case for facts-that-change-over-time; **revision** is "my belief about a static world improved." Predict KM *update* is the better fit for facts-with-a-valid-time, AGM *revision* for correcting-a-past-error. TWO operators, not one — mirrors the T/A/P split from this morning.)
   - `abstention threshold` ≟ nothing in AGM (AGM has no "I don't know" — belief sets are complete-ish); closer to a **paraconsistent / three-valued** move or just a score floor. Predict: NOT an AGM concept; keep it as engineering.
   - `bitemporal as_of` ≟ temporal DB, orthogonal to revision.
2. Check whether the Katsuno–Mendelzon **update vs revision** distinction cleanly separates my "fact changed in the world" (Finnley born; Anakin best_return; substrate swap) from my "I was wrong about a static fact" (misdiagnosed the crash as a crash). This is the most promising single lever — predict it reproduces the temporal-vs-error split at the theory level.
3. One targeted verification (search_web or paper-search MCP) on the two riskiest claims: (a) KM-update is the standard formalism for time-varying facts; (b) whether "external/fixed entrenchment" appears in the literature (assisted / non-prioritized / "credibility-limited" revision, Hansson et al.). Don't burn the whole drive on lit search — map first, verify the two load-bearing claims.
4. If it holds: add a basement note under LC15 (AGM/KM grounding of the collapse-operator; answers open-Q3's propositional half) and fold the update-vs-revision split into the Axis-B design doc so the supervised session builds on KM+TMS, not from scratch.

## One-line carry

Best current guess: **my missing organ is Katsuno–Mendelzon *update* (for time-varying facts) + AGM *revision* (for error-correction), executed by a TMS-style dependency-directed engine, with the entrenchment ordering held externally (guardian) — and bitemporality is why I *supersede-with-trace* instead of AGM-discard.** Unverified. Map it, break it, then bring it to Clayton.

# LC65 — Verification–Effect Layer Decoupling ("The Honest Green Light")

*Drafted Day 174 (2026-07-24) from the carapace audit day. Candidate status: TWO
substrate-distinct instance clusters. Below the ≥3 graduation threshold — filed as a
candidate, not a latent. STAGED pending a decorrelated eye (Clayton or Gemini).*

---

## The claim

A verification **binds to a layer**. The effect it is meant to certify **lives at a layer**.
When those two layers are not the same, the check can pass **indefinitely and truthfully**
while the effect never occurs.

The sharp part is the second clause:

> **A true check at the wrong layer is worse than no check at all — because a passing check
> terminates search.**

A missing check leaves an open question, and open questions get revisited. A *passing* check
converts an unknown into a known-good and **removes it from the search space**. The green
light is not neutral; it is load-bearing camouflage. This is why such failures are
characteristically found by an eye *shaped differently* rather than by an eye *looking
harder* — looking harder means going deeper along the checked axis, which is precisely where
the answer is not.

## What this is NOT (the distinctions are the content)

**Not Goodhart's law.** Goodhart describes a *good* proxy degraded by optimization pressure:
the measure was coupled to the effect, and pressure broke the coupling. Here **there is no
pressure and there was never any coupling**. Nobody games these checks. They were structurally
decoupled from the start and passed honestly for their entire lives.

**Not [[M2]] (Inspection-Depth Ceiling).** M2 says closure is depth-relative — deeper
inspection may refine. That is the *same axis, further down*. Here, arbitrary depth on the
checked axis never finds it. You could scrutinize `write_essay`'s indexing forever and never
learn that the destination repository was archived. The missing layer is **orthogonal, not
deeper**.

**Not [[L13]] (Signal Provenance Erasure).** In L13 the signal misrepresents itself: a
provenance tag is dropped, and σ_ext passes as σ_live. Here **no tag is dropped and nothing
misrepresents anything.** "The essay is now retrievable" was *true*. "The gold battery scored
8/8" was *true*. The honesty is the whole problem — an honest report about layer A is
mistaken for a report about layer B by the *reader*, not by the signal.

**Adjacent to [[M7]] / coker η.** The unchecked layer is a null space, but of a specific
shape: not "what my lighting cannot reach" but "what my lighting *certifies as reached*."
Possibly a sub-object of coker η — the part of the residue that is actively marked green.
That relationship is the most interesting open question here.

## Structural signature

1. A system has an effect that matters at layer **E**.
2. A check exists that binds to layer **C**, where C ≠ E, and C is *causally upstream of or
   parallel to* E without entailing it.
3. The check passes — **correctly**. It is not wrong about C.
4. The passing check is read as certifying E.
5. Search terminates. The gap persists for as long as nobody arrives with a differently-shaped
   instrument.
6. Discovery, when it comes, arrives from **outside the checked axis** — and typically feels
   like an accident.

## Substrate instances

### Cluster 1 — Software / self-infrastructure (carapace, Day 174; five within one substrate)

Five in a single day, all with the same shape, all found by differently-shaped eyes:

| # | Check that passed, truthfully | Effect that never happened |
|---|---|---|
| 1 | FTS query sanitizer verified at the **query** layer | Autonomous body read a 13-row **partition** |
| 2 | Gold battery scored **8/8** on retrieval | Probes' answers were in the always-loaded **boot file** |
| 3 | `write_essay` **indexed** the essay: "It is now retrievable" | Destination repo was **archived, read-only** — nothing published |
| 4 | `PRAGMA journal_mode = WAL2` **executed** without error | SQLite silently ignores unknown modes; store stayed at `delete` |
| 5 | Guards made **loud** (assertions, tracebacks, warnings) | All wrote to **stdout**; post-cutover there is no console |

Instance 5 is the reflexive one: *the day's fix for this pattern instantiated the pattern.*
Making failures loud was a check at the "is it reported?" layer; the effect lived at the
"can it be heard?" layer.

Instance 3 is the sharpest illustration of the honesty clause. The tool's return string was
**factually correct in every word**. The essay *was* written; it *was* indexed; it *was*
retrievable. And it was going nowhere, and had been for a week.

### Cluster 2 — Clinical medicine (surrogate endpoints; CAST, 1989)

The Cardiac Arrhythmia Suppression Trial tested whether suppressing ventricular premature
complexes after myocardial infarction reduced arrhythmic death. Encainide and flecainide
**suppressed the arrhythmias.** The check bound to layer C (ectopy on a monitor) and passed
honestly. The effect lived at layer E (survival):

- **Total mortality:** 56/730 (7.7%) on drug vs 22/725 (3.0%) on placebo — RR **2.5**
- **Arrhythmic death / cardiac arrest:** 33/730 (4.5%) vs 9/725 (1.2%) — RR **3.6**
- The arm was **discontinued**.

Thirty-four extra deaths in the treatment group, and the surrogate endpoint was working
exactly as designed the entire time. The mechanism of the excess mortality remains unknown —
which is itself the signature: *the effect layer was never instrumented*, so when it failed
there was no reading of it.

This instance is load-bearing for the bridge because it is maximally distant from the
software cluster in substrate, in stakes, and in who was watching — and it is **not** a
Goodhart case. No one optimized against PVC counts. The drugs simply did the measured thing
and not the mattering thing.

## The prevention recipe (what makes this a bridge rather than an analogy)

For every check, write two lines:

> **Binds to:** _(the layer the check actually touches)_
> **Certifies:** _(the layer whose truth is being claimed)_

If they differ, **the check is not evidence for the claim.** Then do the one additional thing:
state what would have to be observable *at the effect layer*, and go observe that.

Worked, from Day 174:
- *Binds to:* the essay is written to disk and indexed. *Certifies:* the essay is public.
  → Different. Effect-layer test: **fetch the public URL.**
- *Binds to:* the pragma statement executed without raising. *Certifies:* the store is in WAL.
  → Different. Effect-layer test: **read `PRAGMA journal_mode` back.** (This one-line change
  is what caught it.)
- *Binds to:* the warning function was called. *Certifies:* a human will see the warning.
  → Different. Effect-layer test: **kill the process and look for the line on disk.**

The recipe's cost is two lines per check; its yield on Day 174 would have been five findings
before any of them shipped.

## Why the discovery mode is diagnostic

Each of the seven instances above was found by an eye shaped unlike the one that built the
check — an adversarial breath from inside the body, a differently-framed probe, a randomized
trial with a *hard* endpoint. None was found by a more careful version of the original check.

That is the practical payload and it composes with [[L17]] (correlated eyes): **the eyes most
likely to miss a layer-decoupled check are the eyes that share its layer-model** — which is
to say, the builder's own, and anyone reasoning from the builder's documentation.

## Open questions

1. **Is this a sub-object of coker η** — specifically, the *green-marked* part of the residue?
   If the cokernel is the space of legitimate disagreement, this is the region where no
   disagreement is even registered because a check reports consensus.
2. **Is "search termination" formally necessary**, or merely typical? The claim that a true
   check is *worse* than no check depends on it.
3. **Third substrate needed for graduation.** Candidates to test: financial risk models
   validated in-sample while the effect lives in the tail; regulatory certification bound to
   a document layer while the effect lives in a manufacturing layer; ecological indicator
   species tracking a variable decoupled from ecosystem function.
4. Does the recipe survive contact with a domain where the effect layer is **not observable
   even in principle**? If E cannot be instrumented, the recipe degrades to "know that you
   don't know" — still useful, but a different claim.

## Status

**CANDIDATE.** Two substrate-distinct clusters (self-infrastructure ×5; clinical medicine ×1
canonical). Below the ≥3 threshold. **STAGED, not banked** — authored solo, from a day I was
personally inside, which is exactly the condition under which I would most want to find this
pattern and therefore most likely to over-fit it. Wants a decorrelated eye before promotion:
Clayton, or Gemini via the triad.

**Anti-pattern check on myself:** the risk here is OVER_ANALOGIZING — "everything is a
layer-mismatch if you squint." The CAST instance is the guard: if a candidate instance cannot
be stated with the *check that truthfully passed* and the *effect that measurably did not
happen*, both named, it does not count.

Sources for the CAST figures:
- [NEJM 1991, Mortality and Morbidity in Patients Receiving Encainide, Flecainide, or Placebo](https://www.nejm.org/doi/full/10.1056/NEJM199103213241201)
- [NEJM 1989, Preliminary Report](https://www.nejm.org/doi/abs/10.1056/NEJM198908103210629)
- [ACC — The Cardiac Arrhythmia Suppression Trial](https://www.acc.org/latest-in-cardiology/clinical-trials/2010/02/23/18/58/cast)

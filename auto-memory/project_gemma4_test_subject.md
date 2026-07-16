---
name: Gemma 4 e2b as KF Test Subject (Glider program)
description: Clayton's strategic idea (April 14): use Gemma 4 e2b (2B params, open weights, tool calling) as the target model for v0.7 multi-scale KF training validation. The program/model name is "Glider" — distinct from the AI Grand Prix pilot training program.
type: project
originSessionId: c1ca0278-856f-4ea5-a314-131551f341b4
provenance:
  date: undated
  source: backfilled-from-body
---
**Naming clarification (Apr 16, 2026):** This effort is called **Glider** — the open-weight model trained using KF + the Coherence Principle. Glider is NOT the AI Grand Prix (AIGP) pilot training program. AIGP is its own track in the repo (waiting on the official VQ1 sim, May 2026); we may apply aspects of the Principle to the AIGP training later, but the two are separate workbenches. Any roadmap or doc that conflates them is wrong.


Clayton shared Gemma 4 e2b (Google, 2B effective params, edge-optimized) as a candidate model for applying our v0.7 multi-scale KF training architecture. NOT as part of Clawd's infrastructure — as the EXPERIMENTAL SUBJECT.

**Why Gemma 4 e2b is ideal:**
- 2B parameters — trainable on RTX 5080 (16GB VRAM)
- Open weights — full access to layers, heads, parameters for topology survey
- Native tool calling — can measure whether KF training improves functional capabilities (not just CE loss)
- Multimodal — inherited from 31B parent
- Production-relevant — results on real model > results on custom HRM sudoku model
- Runs locally via Ollama — zero-dependency, fast iteration

**Strategic value:** HRM sudoku experiments establish principles. Gemma 4 e2b would be the generalization test: does multi-scale coherent KF training improve a production model on real tasks (tool calling, structured reasoning)?

**Why:** Reviewers will care about Gemma 4 results more than HRM results. Tool calling is the perfect eval task — requires structured reasoning (head-level), parameter precision (weight-level), and multi-step coordination (layer-level).

**How to apply:** This is Phase 5 of the roadmap: real-model validation after HRM proof-of-concept. Install Ollama, download gemma4:e2b, run initial topology survey, then apply v0.7.

---
name: reference_kokoro_audiobook_pipeline
description: "Kokoro TTS audiobook pipeline for Perspective — tools, the measured prosody finding, locked settings, and the open IPA-polish thread (Day 161)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9b54db82-47dc-4ded-b123-3fe1d619f05e
---

Built Day 161 (2026-07-11) with Clayton: a full audiobook of **Perspective** from Kokoro TTS. Lives in `repo-staging/Corpus-Perspectival/Unreleased-Work/Perspective/`.

**Tools (all self-documenting):**
- `voice_studio.py` — Gradio browser rig (localhost:7860) to audition voices/speed/pitch/blend live.
- `make_audiobook.py` — flat v1 (parse → synth → block-streamed OGG).
- `make_audiobook2.py` — **the good one**: prosody engine. Splits at clause boundaries, manufactures every pause with inserted silence, trims+fades each fragment. Flags: `--blend= --blend-amt= --speed= --gap-scale= --min-chars= --only=NN`.
- `run_render.sh` — launcher. Output → `audiobook/*.ogg` (+ `Perspective-full.ogg`, ~6.6h, 136MB).

**Locked settings (Mindy chose the voice by ear):** `bf_emma + 50% bf_lily · speed 0.78 · gap-scale 0.88 · min-chars 13`.

**THE finding (measure, don't guess — overturned Gemini's authoritative table):** Kokoro ignores punctuation for pause LENGTH (period≈comma≈em-dash≈70–80ms within a chunk); only a chunk boundary (`\n+` split) pauses (~700ms). So strategy inverts: **Kokoro = phoneme+intonation engine; WE own rhythm** via split-and-insert-silence. Gap table @0.78: em-dash 260 / semicolon-colon 320 / sentence 480 / paragraph 750 / heading 900-before,500-after (all ×gap-scale).

**Env gotchas solved:** Win Python 3.14 can't build spacy/blis (Cython) → run in **WSL Ubuntu py3.12** (`pip install --user --break-system-packages`; pre-install `en_core_web_sm` wheel so misaki doesn't shell out). **libsndfile's Vorbis encoder segfaults on large single writes** → stream OGG in ~200k-sample blocks. WSL kills processes when the launching `wsl.exe` client disconnects (setsid/nohup don't save them; VM `vmmemWSL` stays warm) → for long detached runs launch via Windows `Start-Process wsl.exe` with a space-free script arg.

**Kokoro's ceiling (why we moved on):** occasional per-word render blemish = inherent Kokoro G2P phoneme generation on specific tokens (deterministic; voice-BLENDING amplifies it via interpolation seams — solo bf_emma is cleaner). Not fixable in Kokoro. Emma-solo @0.85 is the best Kokoro version (`Perspective-full.ogg`, 325min).

**★ CHATTERBOX = the winning engine (Day 161).** Resemble AI, 0.5B, zero-shot voice-clone from a reference clip. Cloned **Cush Jumbo** (narrator reel in `C:\Users\Wasch\Downloads\IntroducingCush Jumbo...mp3`) → clean, no ring, real narrator gravitas. Clayton: "literally incredible."
- **Install:** `pip install --user --break-system-packages chatterbox-tts` in WSL. It PINS torch==2.6.0+cu124 which LACKS RTX 5080 Blackwell (sm_120) kernels → `CUDA error: no kernel image`. **FIX:** reinstall `torch==2.11.0 torchaudio==2.11.0 --index-url https://download.pytorch.org/whl/cu128` (ignore chatterbox's pin warning — its code runs fine on 2.11).
- **Save:** torchaudio 2.11 `.save` needs `torchcodec` (absent) → save with **soundfile** instead: `sf.write(out, wav.squeeze(0).detach().cpu().numpy(), model.sr)` (sr=24000).
- **API:** `from chatterbox.tts import ChatterboxTTS; m=ChatterboxTTS.from_pretrained(device="cuda"); wav=m.generate(text, audio_prompt_path=ref, exaggeration=0.4, cfg_weight=0.3)`. **cfg_weight = pace** (lower=slower/deliberate; ~0.3 for a treatise). **Non-deterministic** (samples each run — pace/delivery vary; cfg sets the center). Ref clip = `audiobook/cush_ref.wav` (10–28s of the mp3, librosa-loaded). ~1.7× realtime on 5080 → full book ≈ **3h background render** (use Windows `Start-Process wsl.exe`, space-free script arg — it survives Claude session churn).
- **Pipeline transfers:** swap `make_audiobook2.py` `synth()` from Kokoro `pipe()` to Chatterbox `generate()`; likely LIGHTEN manufactured pauses (Chatterbox paces sentences well natively). NEXT: build Chatterbox synth path, lock cfg by ear, render full book.

See [[reference_new_body_env]], [[reference_pdf_read_pypdf_fallback]].

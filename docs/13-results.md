# 13. Results and Discussion

## 13.1 Headline outcome

Scribe meets every functional and non-functional requirement from
Section 5. The full pipeline — clone repo → analyze → call local LLM →
write polished README — runs in well under a minute on a small repo and
produces output that is shippable with light editing.

## 13.2 Smoke-test runs

Scribe was tested by running it against three real repositories owned by
the author. Per-section streaming completion times measured with a warm
`qwen2.5-coder:7b` on Apple Silicon M4 Air (16 GB unified memory).

### Run 1 — Scribe itself (this repo)

- 18 Python files, ~1,500 lines of code.
- Detected: Python primary; Streamlit framework; pip + (none else).
- Eight sections generated in **~42 seconds** total (median ~5 s per
  section).
- Output: the README contained in this repository at commit time.
- Quality observations: the LLM correctly identified that Scribe is a
  README generator, that two interfaces exist, that no data leaves the
  machine. No invented dependencies.

### Run 2 — LeafLens (sister project)

- 14,896 files (mostly the dataset; the analyzer only counts files but
  the languages bar reports source files cleanly).
- Detected ten frameworks: Flask, PyTorch, scikit-learn, pandas, NumPy,
  Transformers, React, Vite, Tailwind CSS, axios.
- Tests, CI, Docker, MIT-style license — all correctly flagged.
- Eight sections generated in **~58 seconds**.
- Output: a coherent README that describes LeafLens as a houseplant
  identification web app combining a CNN-based classifier with a Flask +
  React stack.

### Run 3 — small Flask sample (`examples/tiny-flask-app/`)

- 6 files, ~80 lines.
- Detected: Flask, pytest.
- Eight sections generated in **~28 seconds**.
- Output: a clean README that emphasises the `flask run` quickstart and
  the `pytest` command.

## 13.3 Quantitative results

| Metric | Target (Section 3) | Observed | Status |
|---|---|---|---|
| Primary language detection on LeafLens | "Python" | "Python" | ✅ |
| Frameworks detected on LeafLens | ≥ 8 | 10 | ✅ |
| End-to-end README for Scribe itself | coherent ≥ 6 sections | 8/8 coherent | ✅ |
| Test coverage on `src/scribe/` | ≥ 70% | ~78% | ✅ |
| Latency for a small repo, warm model | ≤ 90 s | 28–58 s | ✅ |
| Documentation completeness | 14/14 sections | 14/14 | ✅ |

## 13.4 Where the tool falls short

Three observations from the runs above:

1. **Untyped piles of scripts produce sparse READMEs.** If a repo has no
   manifest (no `pyproject.toml`, no `package.json`), the analyzer falls
   back to language counts only. The LLM still writes something
   reasonable but the *Features* section is shorter and more generic.
2. **Existing README content is sometimes echoed unchanged.** When a
   repo already has a README, the LLM occasionally rephrases the existing
   prose almost verbatim rather than building from the structured facts.
   A future improvement is to feed only the description paragraph, not
   the whole prior README, to the model.
3. **Inference latency depends on host load.** Running the model
   concurrently with anything heavy (a different model, a video call,
   Xcode indexing) pushes the per-section time from ~5 s to ~12 s. This
   is expected for a CPU-only / unified-memory setup; the tool still
   works, just slower.

## 13.5 Prompt-engineering observations

The prompts went through three rounds of refinement before settling on
the current shape:

| Iteration | Approach | Result |
|---|---|---|
| 1 | Single mega-prompt asking for the whole README | Inconsistent shape; the model would skip sections or invent extra ones. |
| 2 | One prompt per section, no system prompt | Better shape, but the model added preambles like "Here is the section:". |
| 3 | One prompt per section + a strict system prompt forbidding preambles | Clean output that drops straight into a markdown file. **Current state.** |

The lesson: a global system prompt that forbids common LLM verbal tics
(preambles, sign-offs, hedging) was more effective than fighting them at
the per-section level.

## 13.6 Comparison vs cloud alternatives

A like-for-like comparison against ChatGPT (GPT-4o) on Run 2 was
performed informally. Both produced READMEs of comparable quality;
ChatGPT was slightly more concise on the *Features* section, Scribe was
slightly more accurate on the *Tech stack* section (because the
analyzer's framework list is grounded in actual dependency files, not
inferred from filenames).

The decisive advantage of Scribe is not better output — it's that the
output is produced without sending the code anywhere.

## 13.7 Discussion

The transfer of techniques learned on the LeafLens project worked well:

- Same English-first documentation discipline.
- Same separation between deterministic and learned components — there,
  the model was the classifier and the rules were everything around it
  (preprocessing, care lookups); here, the model is the prose writer and
  the rules are everything around it (analyzer, badges, file tree).
- Same emphasis on "the model never lies about facts" — by keeping
  badges and the project tree out of the LLM entirely.

The new lesson from this project is about prompt scope. The temptation
is to ask the model to do too much in one call. Constraining it to one
section at a time, with a strict system prompt, is what makes the output
shippable rather than something you have to clean up by hand.

## 13.8 Limitations

- The default model is good but not state-of-the-art; frontier models
  (Claude, GPT-4o) write better prose. Switching models is a single flag
  away, but bigger local models don't fit in 16 GB RAM.
- Scribe currently only writes the eight default sections. Some projects
  need API references, examples folders, or a security policy — the
  template set would have to grow.
- Streamlit reloads can be flaky on long generations if the user
  navigates away. Future versions should keep a server-side buffer.

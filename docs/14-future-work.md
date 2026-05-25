# 14. Recommendations and Future Work

## 14.1 Recommendations

### For users

- **Pull the model once, then go offline.** The whole point of Scribe is
  that nothing else needs to happen over the network. Pull
  `qwen2.5-coder:7b` once and it's yours forever.
- **Edit the generated README.** Scribe is a draft-writer. Two minutes of
  hand-editing turns a B+ output into an A.
- **Re-run periodically.** As your project gains dependencies and CI,
  regenerate the README and diff it against the committed version.
- **Try other models.** `--model llama3.2:3b` is twice as fast at the
  cost of slightly more generic prose, and runs on smaller machines.

### For maintainers of Scribe

- Keep `prompts.py` versioned and changelog-style commented. Prompt
  regressions are easy to miss; treat them like any other code change.
- Treat the analyzer as the source of truth. Anything the model
  hallucinates can usually be removed by tightening the prompt to "only
  use facts from the provided block".

## 14.2 Future work

### Short term (one to three months)

- **Confluence / GitHub Pages export.** Once a project has a README,
  pushing it as a wiki page is a small step.
- **Diff-aware mode.** If a `README.md` already exists, Scribe could
  surface a per-section diff instead of overwriting, so maintainers
  accept changes selectively.
- **Section plugins.** Allow third parties to drop a new prompt module
  into `src/scribe/prompts/` and have Scribe register it automatically —
  useful for project-specific sections (e.g. a *Deployment* section that
  reads `render.yaml` and a *Releases* section that reads
  `CHANGELOG.md`).
- **README quality checks.** Run a linter on the generated markdown
  (broken links, missing alt text, code blocks without language tags) and
  loop the model back to fix issues until clean.

### Medium term (three to twelve months)

- **Multi-language output.** Generate the README in English and then
  produce localized versions (Spanish, Portuguese, French) by re-prompting
  per section.
- **`pre-commit` hook.** Automatically regenerate the README in CI
  whenever the underlying facts change (new dependencies, new entry
  points). Block PRs whose READMEs are stale.
- **VS Code extension.** Wrap the engine in a tiny extension that adds
  "Scribe: Generate README" to the command palette.
- **Web demo with bring-your-own-model.** A hosted UI where the user
  pastes an `OLLAMA_HOST` and Scribe talks to their tunnel. Keeps the
  privacy property while removing the local install step.

### Long term (one year or more)

- **Repo-wide documentation.** Beyond the README, generate
  `CONTRIBUTING.md`, `SECURITY.md`, architecture diagrams, and module
  docstrings — all from the same analyzer + LLM core.
- **API reference autogeneration.** For projects that already use type
  hints, build a docs site (Sphinx / TypeDoc) and have Scribe write the
  narrative around it.
- **Active doc maintenance agent.** A long-running watcher that catches
  changes in `package.json` / `pyproject.toml`, regenerates the affected
  sections, and opens a draft PR.

## 14.3 Lessons learned

- **Section-scoped prompts beat mega-prompts.** Trying to make the model
  produce the whole README in one shot is a losing battle on a 7 B model.
  One section, one prompt, one focused output — the rest of the day was
  obvious after that landed.
- **Keep facts and prose separate.** The model writes prose; the
  analyzer writes facts. Mixing the two means the model will eventually
  hallucinate a "fact" you didn't give it.
- **System prompts win.** A short, strict system prompt that forbids
  preambles and AI tics improved the quality of every section without
  touching the section prompts themselves.
- **Local-LLM is a real selling point now.** Two years ago this would
  have been a hobby project; today `qwen2.5-coder:7b` produces output a
  busy maintainer would actually keep.
- **Reusing patterns from LeafLens cut work in half.** The setup script,
  the cleanup script, the doc structure, the slide template — none of
  these had to be designed twice. That kind of compounding is the
  argument for keeping a personal style guide across projects.

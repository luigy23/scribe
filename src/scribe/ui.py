"""Streamlit web UI for Scribe — dark mode, cancellable.

Run with: scribe ui  (or: streamlit run src/scribe/ui.py)

Architecture:
- Single column, dark palette.
- Section-by-section generation. Each section completes, the page reruns,
  the next section starts. This means the user can press 'Stop' between
  sections (max ~5–8 s wait).
- Already-generated sections stay visible while the next one streams.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from scribe.analyzer import RepoAnalyzer
from scribe.generator import ReadmeGenerator
from scribe.llm import DEFAULT_MODEL, OllamaClient
from scribe.prompts import SECTION_ORDER
from scribe.templates import render_badges, render_project_structure

# ============================================================================
# Page config
# ============================================================================

st.set_page_config(
    page_title="Scribe — README generator",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================================
# Dark theme
# ============================================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:         #0F1419;
  --surface:    #1A1F2A;
  --surface-2:  #232936;
  --surface-3:  #2D3748;
  --border:     #2D3748;
  --border-soft:#1F2937;
  --text:       #E5E7EB;
  --text-soft:  #CBD5E1;
  --muted:      #94A3B8;
  --dim:        #64748B;
  --amber:      #F59E0B;
  --amber-soft: #FBBF24;
  --green:      #34D399;
  --red:        #F87171;
  --cyan:       #22D3EE;
}

/* Hide all Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
[data-testid="stDecoration"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebar"] { display: none !important; }

/* App background */
html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--text) !important;
}
.main .block-container {
  max-width: 800px;
  padding-top: 2.5rem;
  padding-bottom: 4rem;
}

/* Typography */
body, .stApp, .stMarkdown, p, span, div, label {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--text);
}
h1, h2, h3, h4 {
  font-family: "Fraunces", Georgia, serif;
  font-weight: 600;
  letter-spacing: -0.015em;
  color: var(--text);
  margin: 0;
}
code, pre, .mono { font-family: "JetBrains Mono", "SF Mono", Menlo, monospace; }
code:not(pre code) {
  background: var(--surface-2);
  padding: 1px 6px;
  border-radius: 4px;
  border: 1px solid var(--border);
  font-size: 0.88em;
  color: var(--amber-soft) !important;
}
a { color: var(--amber); }

/* Hero */
.scribe-brand {
  color: var(--amber);
  font-family: "JetBrains Mono", monospace;
  font-size: 13px;
  text-align: center;
  margin-bottom: 6px;
  letter-spacing: 0.04em;
}
.scribe-hero h1 {
  font-size: 56px;
  line-height: 1.0;
  margin: 0 0 14px;
  text-align: center;
}
.scribe-hero h1 em {
  display: block;
  color: var(--amber);
  font-style: italic;
  font-weight: 500;
  margin-top: 4px;
}
.scribe-hero p {
  text-align: center;
  color: var(--muted);
  font-size: 17px;
  line-height: 1.55;
  max-width: 580px;
  margin: 0 auto 24px;
}

/* Status pill */
.scribe-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: "JetBrains Mono", monospace;
  font-size: 12px;
  letter-spacing: 0.02em;
  margin: 0 auto 32px;
  padding: 6px 14px;
  width: fit-content;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
}
.scribe-status.ok { color: var(--green); border-color: rgba(52, 211, 153, 0.3); }
.scribe-status.err { color: var(--red); border-color: rgba(248, 113, 113, 0.4); }
.scribe-status .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 8px currentColor;
}

/* Labels */
.scribe-label {
  display: block;
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
  letter-spacing: 0.06em;
  color: var(--muted);
  margin: 24px 0 8px;
  text-transform: uppercase;
}

/* Text input */
.stTextInput > div > div > input {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 12px 14px !important;
  font-family: "JetBrains Mono", monospace !important;
  font-size: 14px !important;
  color: var(--text) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--dim) !important; }
.stTextInput > div > div > input:focus {
  border-color: var(--amber) !important;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15) !important;
}
.stTextInput label { display: none !important; }

/* Buttons */
.stButton > button {
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 8px 14px !important;
  font-family: "JetBrains Mono", monospace !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  letter-spacing: 0.02em !important;
  transition: all 0.15s ease !important;
}
.stButton > button:hover {
  border-color: var(--amber) !important;
  color: var(--amber) !important;
  background: var(--surface-2) !important;
}
.stButton > button:focus {
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15) !important;
  outline: none !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
  background: var(--amber) !important;
  color: var(--bg) !important;
  border-color: var(--amber) !important;
  font-family: "Inter", sans-serif !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  padding: 14px 24px !important;
  letter-spacing: -0.01em !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--amber-soft) !important;
  color: var(--bg) !important;
  border-color: var(--amber-soft) !important;
  transform: translateY(-1px);
}
.stButton > button[kind="primary"]:disabled {
  background: var(--surface-2) !important;
  color: var(--dim) !important;
  border-color: var(--border) !important;
  cursor: not-allowed;
}

/* Stop button (destructive look) */
.scribe-stop-zone .stButton > button {
  background: var(--surface) !important;
  color: var(--red) !important;
  border-color: rgba(248, 113, 113, 0.3) !important;
  font-family: "JetBrains Mono", monospace !important;
  font-size: 12px !important;
}
.scribe-stop-zone .stButton > button:hover {
  background: rgba(248, 113, 113, 0.1) !important;
  color: var(--red) !important;
  border-color: var(--red) !important;
}

/* Progress */
.stProgress > div > div { background: linear-gradient(90deg, var(--amber), var(--amber-soft)) !important; }
.stProgress > div {
  background: var(--surface-2) !important;
  border-radius: 4px !important;
}
.stProgress > div > div > div { color: var(--muted) !important; font-family: "JetBrains Mono", monospace !important; font-size: 12px !important; }

/* Spinner */
[data-testid="stSpinner"] > div {
  border-top-color: var(--amber) !important;
}

/* Pills */
.scribe-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0;
}
.scribe-pill {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  color: var(--text-soft);
  font-family: "JetBrains Mono", monospace;
}
.scribe-pill strong {
  color: var(--amber);
  font-weight: 600;
  margin-right: 4px;
}

/* Section ticker */
.scribe-ticker {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 16px 0 20px;
}
.scribe-tick {
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
  padding: 4px 12px;
  border-radius: 999px;
  background: var(--surface);
  color: var(--dim);
  border: 1px solid var(--border);
  transition: all 0.2s ease;
}
.scribe-tick.active {
  background: var(--amber);
  color: var(--bg);
  border-color: var(--amber);
  animation: tick-pulse 1.4s ease-in-out infinite;
  box-shadow: 0 0 14px rgba(245, 158, 11, 0.4);
}
.scribe-tick.done {
  background: rgba(52, 211, 153, 0.1);
  color: var(--green);
  border-color: rgba(52, 211, 153, 0.4);
}
@keyframes tick-pulse {
  0%, 100% { box-shadow: 0 0 14px rgba(245, 158, 11, 0.4); }
  50%      { box-shadow: 0 0 24px rgba(245, 158, 11, 0.7); }
}

/* README preview card */
.scribe-result-frame {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 28px 32px;
  margin-top: 16px;
  box-shadow: 0 4px 14px -8px rgba(0, 0, 0, 0.5);
  color: var(--text);
}
.scribe-result-frame h1 { font-size: 32px !important; margin-top: 0 !important; color: var(--text) !important; }
.scribe-result-frame h2 { font-size: 22px !important; margin-top: 28px !important; color: var(--text) !important; }
.scribe-result-frame h3 { font-size: 17px !important; margin-top: 18px !important; color: var(--text-soft) !important; }
.scribe-result-frame h4 { font-size: 15px !important; color: var(--text-soft) !important; }
.scribe-result-frame p, .scribe-result-frame li { font-size: 14px; line-height: 1.6; color: var(--text-soft); }
.scribe-result-frame em { color: var(--amber); }
.scribe-result-frame strong { color: var(--text); }
.scribe-result-frame pre {
  background: var(--bg) !important;
  color: var(--cyan) !important;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px !important;
  font-size: 13px;
  overflow-x: auto;
}
.scribe-result-frame code { color: var(--amber-soft) !important; background: var(--surface-2); }
.scribe-result-frame hr { border-color: var(--border); }
.scribe-result-frame a { color: var(--amber); }
.scribe-result-frame ul { padding-left: 20px; }
.scribe-result-frame img { max-width: 100%; }
.scribe-result-frame blockquote {
  border-left: 3px solid var(--amber);
  padding-left: 14px;
  color: var(--text-soft);
  font-style: italic;
  margin: 14px 0;
}

/* Currently-streaming section indicator (the one growing) */
.scribe-streaming-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  margin: 8px 0;
  border-radius: 8px;
  background: rgba(245, 158, 11, 0.07);
  border: 1px solid rgba(245, 158, 11, 0.3);
  font-family: "JetBrains Mono", monospace;
  font-size: 12px;
  color: var(--amber);
}
.scribe-streaming-banner .pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--amber);
  animation: pulse-glow 1s ease-in-out infinite;
}
@keyframes pulse-glow {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--amber); }
  50%      { opacity: 0.5; box-shadow: 0 0 4px var(--amber); }
}

/* Alert dark theme */
.stAlert {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}
.stAlert[data-baseweb="notification"][kind="error"] {
  border-color: rgba(248, 113, 113, 0.4) !important;
  background: rgba(248, 113, 113, 0.08) !important;
}

/* Expander */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}
[data-testid="stExpander"] details {
  background: transparent !important;
}
[data-testid="stExpander"] summary {
  color: var(--muted) !important;
  font-family: "JetBrains Mono", monospace !important;
  font-size: 12px !important;
}
[data-testid="stExpander"] summary:hover { color: var(--amber) !important; }

/* JSON view */
[data-testid="stJson"] {
  background: var(--bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}
[data-testid="stJson"] * { color: var(--text-soft) !important; }

/* Download button */
.stDownloadButton > button {
  background: var(--amber) !important;
  color: var(--bg) !important;
  border-color: var(--amber) !important;
  font-family: "Inter", sans-serif !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  padding: 12px 20px !important;
}
.stDownloadButton > button:hover {
  background: var(--amber-soft) !important;
  border-color: var(--amber-soft) !important;
}

/* Footer */
.scribe-footer {
  text-align: center;
  color: var(--dim);
  font-size: 12px;
  margin-top: 56px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}
.scribe-footer a { color: var(--muted); text-decoration: none; font-family: "JetBrains Mono", monospace; }
.scribe-footer a:hover { color: var(--amber); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ============================================================================
# Session state
# ============================================================================

# phase ∈ {"idle", "analyzing", "running", "done", "cancelled"}
# pending: list of sections remaining
# done: list of (section_name, generated_content) for sections already produced
# active_section: the one currently being generated, or None
defaults = {
    "phase": "idle",
    "path": "",
    "facts": None,
    "pending": [],
    "done": [],
    "active_section": None,
    "error": None,
    "cancel_requested": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================================================
# Helpers
# ============================================================================


@st.cache_resource(show_spinner=False)
def get_client() -> OllamaClient:
    return OllamaClient(model=os.environ.get("SCRIBE_MODEL", DEFAULT_MODEL))


def render_status():
    client = get_client()
    ok, msg = client.ready()
    if ok:
        st.markdown(
            f"""
            <div class="scribe-status ok">
              <span class="dot"></span>
              <span>{client.model} ready · localhost:11434</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="scribe-status err">
              <span class="dot"></span>
              <span>{msg}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()


def discover_recent_repos(limit: int = 4) -> list[Path]:
    candidates: list[Path] = []
    for root in [
        Path.home() / "Documents" / "GitHub",
        Path.home() / "code",
        Path.home() / "projects",
    ]:
        if root.exists():
            for child in root.iterdir():
                if child.is_dir() and not child.name.startswith("."):
                    if (
                        (child / ".git").exists()
                        or (child / "pyproject.toml").exists()
                        or (child / "package.json").exists()
                    ):
                        candidates.append(child)
    candidates.sort(key=lambda p: -p.stat().st_mtime)
    return candidates[:limit]


def render_pills(facts) -> str:
    pills = [
        f'<span class="scribe-pill"><strong>{facts.total_files:,}</strong> files</span>',
        f'<span class="scribe-pill"><strong>{len(facts.languages)}</strong> languages</span>',
        f'<span class="scribe-pill"><strong>{len(facts.frameworks)}</strong> frameworks</span>',
    ]
    if facts.primary_language:
        pills.append(
            f'<span class="scribe-pill">primary: <strong>{facts.primary_language}</strong></span>'
        )
    if facts.license_name:
        pills.append(
            f'<span class="scribe-pill">license: <strong>{facts.license_name}</strong></span>'
        )
    if facts.has_tests:
        pills.append('<span class="scribe-pill">tests ✓</span>')
    if facts.has_ci:
        pills.append('<span class="scribe-pill">CI ✓</span>')
    if facts.has_dockerfile:
        pills.append('<span class="scribe-pill">Docker ✓</span>')
    return f'<div class="scribe-pills">{"".join(pills)}</div>'


def render_ticker(active: str | None, done_sections: list[str]) -> str:
    done_set = set(done_sections)
    chips = []
    for s in SECTION_ORDER:
        cls = "done" if s in done_set else ("active" if s == active else "")
        chips.append(f'<span class="scribe-tick {cls}">{s}</span>')
    return f'<div class="scribe-ticker">{"".join(chips)}</div>'


def assemble_readme() -> str:
    """Combine all done sections (including injected badges + tree) into final markdown."""
    parts: list[str] = []
    for section, content in st.session_state.done:
        parts.append(content.strip())
    return "\n\n".join(parts) + "\n"


def reset_to_idle():
    for k, v in defaults.items():
        if isinstance(v, list):
            st.session_state[k] = []
        elif isinstance(v, set):
            st.session_state[k] = set()
        elif isinstance(v, bool):
            st.session_state[k] = False
        else:
            st.session_state[k] = v


# ============================================================================
# Layout — hero + status (always visible)
# ============================================================================

st.markdown(
    """
    <div class="scribe-hero">
      <div class="scribe-brand">~/scribe</div>
      <h1>Every repo deserves<br><em>a good README.</em></h1>
      <p>Point Scribe at a folder. Get a polished README back. The model runs on your own machine — no API key, no cloud, no data leaves the laptop.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

render_status()

# ============================================================================
# IDLE — path input + generate
# ============================================================================

if st.session_state.phase == "idle":
    st.markdown('<span class="scribe-label">Repository path</span>', unsafe_allow_html=True)

    default_path = st.session_state.path or str(Path.home() / "Documents" / "GitHub" / "scribe")
    path_input = st.text_input(
        "Path",
        value=default_path,
        label_visibility="collapsed",
        placeholder="/Users/you/projects/my-repo",
    )

    recents = discover_recent_repos(limit=4)
    if recents:
        st.markdown('<span class="scribe-label">Recent repos</span>', unsafe_allow_html=True)
        cols = st.columns(len(recents))
        for col, repo in zip(cols, recents):
            with col:
                if st.button(repo.name, use_container_width=True, key=f"quick_{repo.name}"):
                    st.session_state.path = str(repo)
                    st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if st.button("Generate README", type="primary", use_container_width=True):
            try:
                resolved = Path(path_input).expanduser().resolve()
                if not resolved.is_dir():
                    st.session_state.error = f"Not a directory: {resolved}"
                else:
                    st.session_state.path = str(resolved)
                    st.session_state.phase = "analyzing"
                    st.session_state.error = None
                    st.session_state.facts = None
                    st.session_state.pending = list(SECTION_ORDER)
                    st.session_state.done = []
                    st.session_state.active_section = None
                    st.session_state.cancel_requested = False
                    st.rerun()
            except (OSError, ValueError) as exc:
                st.session_state.error = f"Could not resolve path: {exc}"

    if st.session_state.error:
        st.error(st.session_state.error)


# ============================================================================
# ANALYZING — quick scan, transitions to RUNNING
# ============================================================================

if st.session_state.phase == "analyzing":
    repo_path = Path(st.session_state.path)

    col_l, col_r = st.columns([4, 1])
    with col_l:
        st.markdown(
            f'<span class="scribe-label">Generating for: <code>{repo_path}</code></span>',
            unsafe_allow_html=True,
        )
    with col_r:
        st.markdown('<div class="scribe-stop-zone">', unsafe_allow_html=True)
        if st.button("Stop", key="stop_analyze", use_container_width=True):
            st.session_state.cancel_requested = True
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.cancel_requested:
        st.session_state.phase = "cancelled"
        st.rerun()

    with st.spinner(f"Analyzing {repo_path.name}…"):
        try:
            facts = RepoAnalyzer(repo_path).analyze()
        except Exception as exc:
            st.error(f"Analyzer failed: {exc}")
            st.session_state.phase = "idle"
            st.session_state.error = str(exc)
            st.stop()

    st.session_state.facts = facts
    st.session_state.phase = "running"
    st.rerun()


# ============================================================================
# RUNNING — one section per rerun, cancellable between sections
# ============================================================================

if st.session_state.phase == "running":
    repo_path = Path(st.session_state.path)
    facts = st.session_state.facts
    total = len(SECTION_ORDER)
    done_count = len([s for s, _ in st.session_state.done if s in SECTION_ORDER])

    # Header with Stop button
    col_l, col_r = st.columns([4, 1])
    with col_l:
        st.markdown(
            f'<span class="scribe-label">Generating for: <code>{repo_path}</code></span>',
            unsafe_allow_html=True,
        )
    with col_r:
        st.markdown('<div class="scribe-stop-zone">', unsafe_allow_html=True)
        if st.button("Stop", key="stop_running", use_container_width=True):
            st.session_state.cancel_requested = True
            st.session_state.phase = "cancelled"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Facts pills
    st.markdown(render_pills(facts), unsafe_allow_html=True)

    # Ticker + progress
    next_section = st.session_state.pending[0] if st.session_state.pending else None
    section_names_done = [s for s, _ in st.session_state.done if s in SECTION_ORDER]
    st.markdown(render_ticker(next_section, section_names_done), unsafe_allow_html=True)
    st.progress(
        done_count / total,
        text=f"{done_count} of {total} sections written",
    )

    # Show currently-streaming banner
    if next_section:
        st.markdown(
            f"""
            <div class="scribe-streaming-banner">
              <span class="pulse"></span>
              <span>Generating <strong>{next_section}</strong>…</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Already-completed sections preview
    if st.session_state.done:
        completed_md = "\n\n".join(content.strip() for _, content in st.session_state.done)
        st.markdown(
            f'<div class="scribe-result-frame">{completed_md}</div>',
            unsafe_allow_html=True,
        )

    # Stop check before LLM call (the user might have clicked Stop on a previous rerun)
    if st.session_state.cancel_requested:
        st.session_state.phase = "cancelled"
        st.rerun()

    # Generate the next section (if any)
    if next_section:
        client = get_client()
        generator = ReadmeGenerator(client)
        try:
            content = generator._render_section(next_section, facts, temperature=0.2)
        except Exception as exc:
            st.error(f"Generation failed for section '{next_section}': {exc}")
            st.session_state.phase = "cancelled"
            st.stop()

        st.session_state.done.append((next_section, content))
        st.session_state.pending.pop(0)

        # Inject deterministic blocks after their anchor sections
        if next_section == "title":
            badges = render_badges(facts)
            if badges:
                st.session_state.done.append(
                    ("__badges__", f'<div align="center">\n\n{badges}\n\n</div>')
                )
        if next_section == "development":
            tree = render_project_structure(facts)
            if tree:
                st.session_state.done.append(("__project_structure__", tree))

        st.rerun()
    else:
        # All sections done
        st.session_state.phase = "done"
        st.rerun()


# ============================================================================
# CANCELLED — show partial result + restart options
# ============================================================================

if st.session_state.phase == "cancelled":
    repo_path = Path(st.session_state.path)
    facts = st.session_state.facts

    st.warning("Generation stopped. Partial result shown below.")

    if facts:
        st.markdown(render_pills(facts), unsafe_allow_html=True)

    if st.session_state.done:
        partial = "\n\n".join(content.strip() for _, content in st.session_state.done)
        st.markdown(
            f'<div class="scribe-result-frame">{partial}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("↻ Resume", use_container_width=True):
            st.session_state.cancel_requested = False
            st.session_state.phase = "running"
            st.rerun()
    with col_b:
        if st.session_state.done:
            partial_md = "\n\n".join(content.strip() for _, content in st.session_state.done) + "\n"
            st.download_button(
                "↓ Download partial",
                data=partial_md,
                file_name=f"{repo_path.name}.README.partial.md",
                mime="text/markdown",
                use_container_width=True,
            )
    with col_c:
        if st.button("← New repo", use_container_width=True):
            reset_to_idle()
            st.rerun()


# ============================================================================
# DONE — final result + download + restart
# ============================================================================

if st.session_state.phase == "done":
    repo_path = Path(st.session_state.path)
    facts = st.session_state.facts

    st.markdown(
        f'<span class="scribe-label">README for: <code>{repo_path}</code></span>',
        unsafe_allow_html=True,
    )

    st.markdown(render_pills(facts), unsafe_allow_html=True)

    full_md = assemble_readme()
    st.markdown(
        f'<div class="scribe-result-frame">{full_md}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    col_d, col_r = st.columns(2)
    with col_d:
        st.download_button(
            "↓ Download README.md",
            data=full_md,
            file_name=f"{repo_path.name}.README.md",
            mime="text/markdown",
            type="primary",
            use_container_width=True,
        )
    with col_r:
        if st.button("← Generate for another repo", use_container_width=True):
            reset_to_idle()
            st.rerun()


# Footer
st.markdown(
    """
    <div class="scribe-footer">
      Scribe runs locally · model never sees the network ·
      <a href="https://github.com/luigy23/scribe" target="_blank">github.com/luigy23/scribe</a>
    </div>
    """,
    unsafe_allow_html=True,
)

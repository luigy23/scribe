"""Streamlit web UI for Scribe.

Run with: scribe ui  (or directly: streamlit run src/scribe/ui.py)
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from scribe.analyzer import RepoAnalyzer, RepoFacts
from scribe.generator import GenerationEvent, ReadmeGenerator
from scribe.llm import DEFAULT_MODEL, OllamaClient
from scribe.prompts import SECTION_ORDER

st.set_page_config(
    page_title="Scribe — README generator",
    page_icon="📝",
    layout="wide",
    menu_items={"About": "Scribe — local-LLM README generator. github.com/luigy23/scribe"},
)

# ----------------------------- styling --------------------------------- #

st.markdown(
    """
    <style>
    .stApp { background: #f7f5f1; }
    h1, h2, h3 { font-family: "Fraunces", Georgia, serif; }
    .scribe-meta { color: #6b6b6b; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- sidebar --------------------------------- #

st.sidebar.title("📝 Scribe")
st.sidebar.caption("Local LLM · Ollama · qwen2.5-coder")

model = st.sidebar.text_input("Model", value=os.environ.get("SCRIBE_MODEL", DEFAULT_MODEL))
temperature = st.sidebar.slider("Temperature", 0.0, 1.5, 0.2, 0.05)

sections_picked = st.sidebar.multiselect(
    "Sections",
    options=list(SECTION_ORDER),
    default=list(SECTION_ORDER),
)

with st.sidebar.expander("Status", expanded=True):
    client = OllamaClient(model=model)
    ok, msg = client.ready()
    if ok:
        st.success(msg)
    else:
        st.error(msg)


# ----------------------------- main ------------------------------------ #

st.title("📝 Scribe")
st.markdown(
    "*Drop a local repository path, get a polished `README.md` back. "
    "The model runs on your own machine through Ollama.*"
)

path_input = st.text_input(
    "Repository path",
    value=str(Path.home() / "Documents" / "GitHub"),
    help="Absolute or `~`-prefixed path to a local repo on your machine.",
)

go_col, _ = st.columns([1, 4])
go = go_col.button("Generate README", type="primary", use_container_width=True, disabled=not ok)

if go:
    try:
        repo_path = Path(path_input).expanduser().resolve()
    except (OSError, ValueError) as exc:
        st.error(f"Could not resolve path: {exc}")
        st.stop()

    if not repo_path.is_dir():
        st.error(f"Not a directory: {repo_path}")
        st.stop()

    # --- analyze ---
    with st.spinner(f"Analyzing {repo_path.name}…"):
        try:
            facts = RepoAnalyzer(repo_path).analyze()
        except (FileNotFoundError, NotADirectoryError) as exc:
            st.error(str(exc))
            st.stop()

    facts_col, gen_col = st.columns([1, 2])

    with facts_col:
        st.markdown("### Repo facts")
        st.metric("Languages", len(facts.languages))
        st.metric("Files", facts.total_files)
        st.metric("Frameworks", len(facts.frameworks))
        with st.expander("Full facts", expanded=False):
            st.json(facts.to_dict())

    # --- generate ---
    with gen_col:
        st.markdown("### Generated README")
        live = st.empty()
        progress = st.progress(0, text="Starting…")
        buffer: list[str] = []
        progress_counter = 0
        total_steps = max(len(sections_picked or list(SECTION_ORDER)), 1)
        generator = ReadmeGenerator(client)

        for event in generator.stream(
            facts,
            sections=sections_picked or list(SECTION_ORDER),
            temperature=temperature,
        ):
            if event.status == "start":
                progress.progress(
                    progress_counter / total_steps,
                    text=f"Generating: {event.section}…",
                )
            if event.status == "delta":
                buffer.append(event.payload)
                live.markdown("".join(buffer))
            if event.status == "done":
                progress_counter += 1
                if event.section in {"badges", "project_structure"}:
                    buffer.append("\n\n" + event.payload + "\n")
                else:
                    buffer.append("\n\n")
                live.markdown("".join(buffer))

        progress.progress(1.0, text="Done.")
        readme_text = "".join(buffer).strip() + "\n"
        st.download_button(
            "Download README.md",
            data=readme_text,
            file_name="README.md",
            mime="text/markdown",
            type="primary",
            use_container_width=True,
        )

else:
    st.info(
        "Enter a path on the left and click **Generate README**.\n\n"
        "Try one of your own projects, or this very project at `~/Documents/GitHub/scribe`."
    )

st.markdown(
    "<div class='scribe-meta'>Scribe runs locally — your code does not leave this machine.</div>",
    unsafe_allow_html=True,
)

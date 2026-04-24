import logging

import streamlit as st

from pipeline import run_research_pipeline, StepId, StepPhase

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
st.markdown(" ")
PRODUCT_NAME = "Re:search"
TAGLINE = "Automated research you can trust"
PIPELINE_CAPTION = "Search → Scrape → Write → Critic"

_STEP_LABELS: dict[StepId, str] = {
    "search": "Searching reliable sources…",
    "scrape": "Scraping deep page content…",
    "write": "Writing detailed report…",
    "critic": "Reviewing final report…",
}

_STEP_ORDER: list[StepId] = ["search", "scrape", "write", "critic"]


def _inject_startup_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --rs-accent: #4f46e5;
                --rs-accent-hover: #4338ca;
                --rs-text: #0f172a;
                --rs-muted: #64748b;
                --rs-surface: #f8fafc;
            }
            .block-container {
                padding-top: 2rem;
                max-width: 960px;
            }
            h1, h2, h3 {
                font-family: ui-sans-serif, system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                letter-spacing: -0.02em;
                color: var(--rs-text) !important;
            }
            .rs-hero {
                font-family: ui-sans-serif, system-ui, "Segoe UI", Roboto, sans-serif;
                margin-bottom: 1.75rem;
            }
            .rs-hero-title {
                font-size: 2rem;
                font-weight: 700;
                color: var(--rs-text);
                margin: 0 0 0.35rem 0;
                letter-spacing: -0.03em;
            }
            .rs-hero-accent {
                color: var(--rs-accent);
            }
            .rs-hero-tagline {
                font-size: 1.05rem;
                color: var(--rs-muted);
                margin: 0 0 0.5rem 0;
                font-weight: 500;
            }
            .rs-hero-caption {
                font-size: 0.9rem;
                color: var(--rs-muted);
                margin: 0;
            }
            [data-testid="stBaseButton-primary"] {
                background-color: var(--rs-accent) !important;
                border-color: var(--rs-accent) !important;
            }
            [data-testid="stBaseButton-primary"]:hover {
                background-color: var(--rs-accent-hover) !important;
                border-color: var(--rs-accent-hover) !important;
            }
            footer { visibility: hidden; height: 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title=f"{PRODUCT_NAME} — Research", layout="wide", page_icon="🔎")

_inject_startup_styles()

st.markdown(
    f"""
    <div class="rs-hero">
        <p class="rs-hero-title"><span class="rs-hero-accent">{PRODUCT_NAME}</span></p>
        <p class="rs-hero-tagline">{TAGLINE}</p>
        <p class="rs-hero-caption">{PIPELINE_CAPTION}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "result_topic" not in st.session_state:
    st.session_state["result_topic"] = None

st.caption("Research topic")
col_topic, col_run = st.columns([5, 1], vertical_alignment="bottom")
with col_topic:
    topic = st.text_input(
        "Topic",
        placeholder="e.g. Carbon capture trends in 2025",
        label_visibility="collapsed",
    )
with col_run:
    run = st.button("Run research", type="primary", disabled=not (topic or "").strip(), use_container_width=True)

if run:
    st.session_state["last_result"] = None
    st.session_state["result_topic"] = None
    lines: list[str] = []
    with st.status("Research pipeline", expanded=True) as status:
        status.update(label="Starting…")

        def on_step(step: StepId, phase: StepPhase, meta: dict | None) -> None:
            if phase == "start":
                prefix = "\n".join(lines)
                status.update(
                    label=(prefix + "\n" + _STEP_LABELS[step]) if prefix else _STEP_LABELS[step]
                )
            elif phase == "end" and meta is not None:
                sec = float(meta["seconds"])
                lines.append(f"✓ {_STEP_LABELS[step]} ({sec:.2f}s)")
                status.update(label="\n".join(lines))

        try:
            pipeline_result = run_research_pipeline(topic.strip(), on_step=on_step)
        except Exception as e:
            status.update(label=f"Error: {e}", state="error")
            st.error(str(e))
            st.stop()
        else:
            status.update(label="\n".join(lines) if lines else "Done", state="complete")
            st.session_state["last_result"] = pipeline_result
            st.session_state["result_topic"] = topic.strip()

result = st.session_state.get("last_result")
result_topic = st.session_state.get("result_topic")

if result:
    saved_topic = (result_topic or "").strip()
    if saved_topic and (topic or "").strip() != saved_topic:
        st.info(
            f"Showing results for a previous run: **{saved_topic}**. "
            "Run again to research the topic in the field above."
        )

    total = float(result.get("total_seconds") or 0.0)
    timings = result.get("timings") or {}

    tab_overview, tab_search, tab_scraped, tab_report, tab_critic = st.tabs(
        ["Overview", "Search", "Scraped", "Report", "Critic"]
    )

    with tab_overview:
        st.metric("Total pipeline time", f"{total:.2f}s")
        st.caption("Per-step duration")
        step_cols = st.columns(4)
        for i, key in enumerate(_STEP_ORDER):
            label = key.title()
            if key in timings and timings[key] is not None:
                step_cols[i].metric(label, f"{float(timings[key]):.2f}s")
            else:
                step_cols[i].metric(label, "—")

    with tab_search:
        st.text_area("Search output", (result.get("search_results") or "")[:4000], height=320, disabled=True)

    with tab_scraped:
        st.text_area("Scraped content", (result.get("scraped_content") or "")[:4000], height=320, disabled=True)

    with tab_report:
        with st.container(border=True):
            st.subheader("Final research report")
            st.markdown(result.get("writer_report") or "")

    with tab_critic:
        with st.container(border=True):
            st.subheader("Critic review")
            st.markdown(result.get("critic_result") or "")

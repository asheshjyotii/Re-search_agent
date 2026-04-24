<div align="center">

<img src="img/image.png" width="100%" alt="Re:search — local multi-agent researcher" />

# Re:search

**Local multi-agent researcher** · automated research you can run on your machine

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.34%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-Multi--agent-16A34A?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM%20API-A855F7?style=for-the-badge)](https://openrouter.ai/)
[![Tavily](https://img.shields.io/badge/Tavily-search%20API-0EA5E9?style=for-the-badge)](https://tavily.com/)

[![Follow @asheshjyotii on Twitter](https://img.shields.io/badge/Follow-%40asheshjyotii-1DA1F2?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0yMy45NTMgNC41N2ExMCAxMCAwIDAxLTIuODI1Ljc3NSA0Ljk1OCA0Ljk1OCAwIDAwMi4xNjMtMi43MjNjLS45NTEuNTU1LTIuMDA1Ljk1OS0zLjEyNyAxLjE4NGE0LjkyIDQuOTIgMCAwMC04LjM4NCA0LjQ4MkM3LjY5IDguMDk1IDQuMDY3IDYuMTMgMS42NCAzLjE2MmE0LjgyMiA0LjgyMiAwIDAwLS42NjYgMi40NzVjMCAxLjcxLjg3IDMuMjEzIDIuMTg4IDQuMDk2YTQuOTA0IDQuOTA0IDAgMDEtMi4yMjgtLjYxNnYuMDZhNC45MjMgNC45MjMgMCAwMDMuOTQ2IDQuODI3IDQuOTk2IDQuOTk2IDAgMDEtMi4yMTIuMDg1IDQuOTM2IDQuOTM2IDAgMDA0LjYwNCAzLjQxNyA5Ljg2NyA5Ljg2NyAwIDAxLTYuMTAyIDIuMTA1Yy0uMzkgMC0uNzc5LS4wMjMtMS4xNy0uMDY3YTEzLjk5NSAxMy45OTUgMCAwMDcuNTU3IDIuMjA5YzkuMDUzIDAgMTMuOTk4LTcuNDk2IDEzLjk5OC0xMy45ODUgMC0uMjEgMC0uNDItLjAxNS0uNjNBOS45MzUgOS45MzUgMCAwMDI0IDQuNTl6Ii8%2BPC9zdmc%2B&logoColor=white)](https://twitter.com/intent/follow?screen_name=asheshjyotii)

</div>

---

## Overview

**Re:search** is a **local multi-agent researcher**: specialist agents run in sequence on your machine (via **LangChain**), while you keep control of keys and data in your own environment. Together they **search** the web, **scrape** a high-signal page, **write** a structured report, and **critique** the draft for quality—exposed as a **Streamlit** UI with an optional **CLI**.

**Agent pipeline:** Search → Scrape → Write → Critic

---

## Architecture

The **local researcher** is orchestrated in one place: the UI calls `run_research_pipeline` in `pipeline.py`, which composes **multiple LangChain agents** (tool-using search and scrape) plus **writer** and **critic** chains, all backed by one chat model through **OpenRouter**. Tavily and target URLs are the only external I/O besides the LLM API—your app process stays local.

```mermaid
flowchart LR
    subgraph ui ["Local UI"]
        APP["Streamlit app\napp.py"]
    end
    subgraph core ["Orchestration"]
        PL["run_research_pipeline\npipeline.py"]
    end
    subgraph agents ["Multi-agent researcher"]
        SA["Search agent\n+ search_query"]
        SCR["Scrape agent\n+ page_fetch"]
        WR["Writer chain"]
        CR["Critic chain"]
    end
    subgraph data ["External services"]
        TV["Tavily API"]
        WEB["Target URLs"]
        OR["OpenRouter\n(LLM)"]
    end

    APP --> PL
    PL --> SA --> SCR --> WR --> CR
    SA --> TV
    SCR --> WEB
    SA --> OR
    SCR --> OR
    WR --> OR
    CR --> OR
```

| Layer | Responsibility |
|--------|----------------|
| **`app.py`** | Local web UI: topic input, live agent-step status, tabs for overview / raw outputs / report / critic. |
| **`pipeline.py`** | Multi-agent sequence: ordered execution, timings, optional `on_step` hooks for progress UI. |
| **`agents.py`** | Agent definitions: `create_agent` for search & scrape; `writer_chain` and `critic_chain` as LCEL pipelines. |
| **`tools.py`** | `search_query` (Tavily), `page_fetch` (HTTP + BeautifulSoup). |
| **`main.py`** | Minimal CLI: stdin topic → same pipeline (no web UI). |

---

## Getting started

### Prerequisites

- **Python 3.11+**
- API keys: **OpenRouter** (LLM) and **Tavily** (web search)

### 1. Clone and environment

```bash
git clone <repo-url>
cd Re-search_agent
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

Using **pip** (project uses `pyproject.toml`):

```bash
pip install -e .
```

Or install from `pyproject.toml` without editable mode:

```bash
pip install .
```

### 3. Configure secrets

Create a **`.env`** file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_key
TAVILY_API_KEY=your_tavily_key
```

Optional OpenRouter branding headers (see LangChain OpenRouter docs): `OPENROUTER_APP_TITLE`, `OPENROUTER_APP_URL`.

### 4. Run the app

**Web UI (recommended):**

```bash
streamlit run app.py
```

Open the URL shown in the terminal (default `http://localhost:8501`), enter a topic, and run **Run research**.

**CLI (headless):**

```bash
python main.py
```

---

## Project layout

```
Re-search_agent/
├── app.py           # Local Streamlit UI for the researcher
├── pipeline.py      # Multi-agent research orchestration
├── agents.py        # LangChain agents + writer/critic chains
├── tools.py         # Tavily search + page fetch tool
├── main.py          # CLI entry
├── pyproject.toml   # Dependencies & metadata
└── README.md
```

---

## Tags & topics

`local-first` · `multi-agent` · `research-agent` · `langchain-agents` · `streamlit` · `openrouter` · `tavily` · `llm` · `python`

---

<div align="center">

<sub>Local multi-agent researcher — LangChain · Streamlit · OpenRouter</sub>

</div>

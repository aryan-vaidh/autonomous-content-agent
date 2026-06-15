# Autonomous Multi-Agent Content Orchestration Engine

An enterprise-grade, asynchronous, multi-agent AI pipeline built using **LangGraph**, **FastAPI**, and **Gemini** to automate the end-to-end process of competitive SEO research, content gap strategy formulation, high-quality article generation, and direct CMS publishing with integrated **Human-in-the-Loop (HITL)** approval via Slack.

---

## 🚀 System Architecture & Core Workflow

The system is designed as a stateful directed acyclic graph (DAG) where specialized agents read from and write to a centralized thread-safe state schema, checkpointed persistently inside an SQLite database.

1. **Inbound Trigger:** A content team member submits a topic via a custom Slack slash command (`/draft <topic>`).
2. **Analyst Agent (`analyst.py`):** Dynamically calls the Serper.dev API to extract the top 10 organic Google ranking URLs, selectively scrapes raw paragraph text from the top 5 competitors using BeautifulSoup4, and synthesizes the data using Gemini to map out the competitive landscape.
3. **Strategist Agent (`strategist.py`):** Analyzes the competitor landscape synthesis to find the "Content Gap." It constructs a 2–3 paragraph execution blueprint detailing off-beat paths, missing value pointers, and targeted user intent formatting.
4. **Writer Agent (`writer.py`):** Ingests the structured strategy and initial topic to craft a massive, high-quality Markdown travel article complete with optimized meta descriptions, high-click titles, and semantic formatting.
5. **Human-in-the-Loop (HITL) Gate:** The LangGraph execution state pauses dynamically before the publication node. A webhook formats and sends interactive interactive block elements (Approve/Reject) directly to a dedicated Slack channel.
6. **Publisher Agent (`publisher.py`):** Upon manual approval, the saved state thread is resumed. A custom structural transformer parses the LLM Markdown text into an exact node-based JSON document mapped to the Wix v3 RichContent REST API schema, uploading it live to the blog dashboard.

---

## 🛠️ Technology Stack

* **Workflow Orchestration:** LangGraph, LangChain
* **State Management & Checkpointing:** SQLite3 (`SqliteSaver`)
* **AI Engine:** Google Gemini API (leveraging `.with_structured_output` via Pydantic)
* **API Framework:** FastAPI, Uvicorn (Asynchronous Background Tasks execution)
* **Data Scrapers:** Serper.dev API, BeautifulSoup4
* **Integrations:** Slack Webhooks & Block Kit UI, Wix CMS REST API
* **CI/CD & Testing:** GitHub Actions, Pytest, Flake8

---

## 📁 Repository Directory Structure

```text
├── .github/
│   └── workflows/
│       └── python-ci.yml       # Automated CI pipeline (Linting & Tests)
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application core & Slack event routing
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # LLM initialization & environment configurations
│   └── agents/
│       ├── __init__.py
│       ├── analyst.py          # Competitor web scraping & data synthesis
│       ├── strategist.py       # SEO blueprinting & gap analysis
│       ├── writer.py           # Creative Markdown generation 
│       ├── publisher.py        # Wix RichContent JSON formatting & REST delivery
│       ├── state.py            # TypedDict definition mapping shared agent memory
│       └── graph.py            # LangGraph pipeline compiling & edge definitions
├── test_main.py                # Pipeline automation verification suite
├── requirements.txt            # Explicit third-party system dependencies
└── README.md                   # System documentation
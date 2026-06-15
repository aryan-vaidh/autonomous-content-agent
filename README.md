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

# ⚙️ Local Installation & Configuration

## 1. Clone & Set Up Environment

```bash
git clone <your-repository-url>
cd BlogAgent

# Create and activate a dedicated virtual environment
python3 -m venv env
source env/bin/activate    # On Windows use: env\Scripts\activate

## 2. Install Project Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Configure Local Environment Variables

Create a `.env` file in the root directory of the project and populate it with your operational credentials:

```env
GEMINI_API_KEY=your_google_gemini_api_key
SERPER_API_KEY=your_serper_dev_search_api_key

SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_SIGNING_SECRET=your_slack_signing_secret

NTX_API_KEY=your_ntx_rest_api_key
NTX_ACCOUNT_ID=your_ntx_account_id
NTX_SITE_ID=your_ntx_site_id
```

---

## 🧪 Continuous Integration & Testing

This project incorporates a continuous integration pipeline via GitHub Actions to maintain code health and strict validation checks on code contributions.

- Linting Engine: **flake8** scans against the repository for critical structural bugs, syntax failures, and cyclomatic complexity limits.

- Testing Engine: **pytest** runs integrated unit and endpoint tests across workflow endpoints.

To run tests and lint checks locally before pushing to remote branches:

```bash
# Run styling and validation lint checks
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Execute the test suite
pytest
```

---

## 🚀 Execution Guide

Start the FastAPI microservice engine locally:

```bash
uvicorn app.main:app --reload
```

The application will spin up a local development server at: `http://127.0.0.1:8000`. Ensure your local host path is securely tunneled (e.g., via `ngrok`) to safely intercept inbound webhook delivery events dispatched from the Slack API servers.

```bash
ngrok http 8000
```

Copy the secure HTTPS URL provided by ngrok and paste it into your Slack App Configuration dashboard under Slash Commands and Interactivity & Shortcuts (e.g., `https://your-ngrok-url.ngrok-free.app/slack/events`).

***

# SEC Filing Research Agent

An auditable, hallucination-resistant Retrieval-Augmented Generation (RAG) system for interrogating SEC 10-K and 10-Q filings. 

Built on a core engineering principle: **The LLM should synthesize evidence, not invent it.**

### Live Deployment
* **Streamlit Web App:** [Launch App](https://sec-filing-agent.streamlit.app/)

* **Interactive Docs (Swagger):** [View API](https://sec-filing-research-agent-399390869297.europe-west1.run.app/docs)

---

## Problem & Solution
Standard RAG pipelines pass every user query into a Vector Database. This works for narrative questions (*"What are Apple's supply chain risks?"*) but fails catastrophically for structured financial questions (*"What was Apple's exact revenue in 2025?"*), leading to LLM hallucinations.

This project utilizes an **Explicit Agent Orchestrator** (built from scratch, without frameworks like LangChain). It deterministically routes narrative questions to a local **ChromaDB** vector store, and numeric questions directly to the **SEC XBRL CompanyFacts API**. The LLM is strictly confined to synthesizing the returned evidence, and a deterministic **Verification Engine** mathematically audits the LLM's final response.

---

## Technology Stack
* **Language:** Python 3.12
* **Web Framework:** FastAPI, Uvicorn, Pydantic
* **AI / ML:** OpenRouter/free , Sentence Transformers (`all-MiniLM-L6-v2`)
* **Vector Database:** ChromaDB
* **Relational Database:** PostgreSQL (Neon Serverless), SQLite (Local), SQLAlchemy ORM
* **Deployment:** Docker, Google Cloud Build, Google Cloud Run
* **Data Sources:** SEC EDGAR (Flat-DOM parsed HTML), SEC XBRL API

---

## System Architecture

Instead of relying on LLM tool-calling, the control flow is entirely deterministic and auditable:

```text
User Question ──► ROUTER
                    │
           ┌────────┴────────┐
        NUMERIC          NARRATIVE
           │                 │
    CAPABILITY CHECK         │
           │                 │
    SEC XBRL API          ChromaDB
           │                 │
           └────────┬────────┘
                    ▼
           PROMPT BUILDER ──► OpenRouter LLM ──► Generated Answer
                                                        │
                 ┌──────────────────────────────────────┘
                 ▼
          CLAIM EXTRACTOR ──► VERIFIER (Math & Lexical Audit)
                                  │
      PostgreSQL Log ◄── Final API Response (Supported / Unsupported)
```

---

## Empirical Evaluation

The system was rigorously benchmarked against a custom adversarial dataset covering 8 major companies (AAPL, MSFT, AMZN, GOOGL, NVDA, TSLA, JNJ, JPM).

| Component | Result | Interpretation |
| :--- | :--- | :--- |
| **Routing Accuracy** | **100%** (12/12) | Perfect classification of Numeric, Narrative, and Hybrid intent. |
| **Capability Accuracy** | **100%** (7/7) | Successfully rejected unsupported metrics (e.g., R&D spend) to prevent hallucination. |
| **Retrieval (Hit@3)** | **100%** | The exact target SEC section was in the top 3 vector results. |
| **Completeness** | **100%** (10/10) | LLM answers were substantive and avoided API safety-filter failures. |
| **Faithfulness Rate** | **100%** | 0% unverified hallucinations. All claims were either mathematically proven (`Supported`) or safely flagged for missing lexical overlap (`Partially Supported`). |

---

Note on LLM Evaluation: Generation was evaluated using OpenRouter's `openrouter/free` endpoint. Because this endpoint dynamically load-balances across available free-tier models (e.g., Llama 3.1 8B, Gemma 2 9B, DeepSeek V4), the underlying model varied between requests. 

The system maintained high faithfulness and completeness across multiple distinct LLM architectures, proving the robustness of the prompt construction and deterministic verification layers.

 The exact model used for each query is captured in the API response and PostgreSQL audit logs.

---

## Core Engineering Principles

1. **Zero LangChain/LlamaIndex:** Orchestration, routing, and tool-dispatch logic are written in pure Python to remain fully transparent and debuggable.

2. **Evidence Before Generation:** The LLM cannot fetch data. It is only handed strictly formatted `Evidence` objects and instructed to cite them (e.g., `[E1]`).

3. **Pessimistic Verification:** The Verifier does not use "LLM-as-a-judge". It uses deterministic float math to verify numbers, and strict lexical overlap to verify narratives.

4. **Out-of-Band Observability:** Every request, route, model slug, latency metric, and verification verdict is asynchronously logged to PostgreSQL without blocking the main Agent reasoning loop.

---

## Local Development

**Clone and Install:**
```bash
git clone https://github.com/YOUR_USERNAME/sec-filing-research-agent.git
cd sec-filing-research-agent
python -m venv .venv
source .venv/bin/activate  # Or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Environment Variables:** Create a `.env` file:
```text
SEC_USER_AGENT="Your Name your.email@example.com"
OPENROUTER_API_KEY="sk-or-v1-..."
# DATABASE_URL="postgresql+psycopg://..." # Optional: Defaults to local SQLite if omitted
```

**Run the API:**
```bash
uvicorn src.api.main:app --reload
```
**Run Streamlit App**
```bash
streamlit run app.py
```

---
*Disclaimer: This is an engineering portfolio project. The corpus is currently limited to FY2025 10-K and 10-Q filings for 8 specific companies and should not be used for actual financial trading decisions.*

***


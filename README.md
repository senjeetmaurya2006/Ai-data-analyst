<div align="center">

# 📊 Autonomous AI End-to-End Data Analyst & BI Agent

**An Enterprise-Grade Multi-Agent Business Intelligence System that transforms raw CSV & Excel datasets into cleaned data, executive KPIs, root-cause diagnostics, interactive dashboards, PDF reports, and PowerPoint decks in seconds.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url-here.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Gemini API](https://img.shields.io/badge/AI%20Brain-Gemini%203.1%20Pro%20%2F%20Flash-8E75B2?logo=google&logoColor=white)](https://ai.google.dev/)
[![Polars](https://img.shields.io/badge/Data%20Engine-Polars-CD792C?logo=polars&logoColor=white)](https://pola.rs/)
[![DuckDB](https://img.shields.io/badge/SQL%20Engine-DuckDB-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Pydantic V2](https://img.shields.io/badge/Validation-Pydantic%20V2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

[**🌐 Live Demo (Streamlit)**](https://your-app-url-here.streamlit.app) • [**📖 Architecture**](#-architecture-philosophy-brain-vs-muscles) • [**🤖 17-Agent Pipeline**](#-the-17-agent-autonomous-ecosystem) • [**🚀 Local Setup**](#-quick-start-local-installation) • [**☁️ Streamlit Cloud Deployment**](#️-deploying-live-on-streamlit-community-cloud)

</div>

---

## 🎯 Project Vision & Overview

Organizations spend up to **80% of their analytics bandwidth** on repetitive tasks: auditing broken schemas, imputing missing values, removing duplicates, writing boilerplate SQL for KPIs, building standard charts, and formatting slides for leadership.

**Autonomous AI Data Analyst** replaces this manual bottleneck with a **17-agent Directed Acyclic Graph (DAG) workflow**. A user simply uploads a `.csv` or multi-sheet `.xlsx` file, and the system autonomously performs the end-to-end work of a **Data Engineer, Data Analyst, BI Developer, and Strategy Consultant**:

1. **Automated Data Profiling & Schema Detection** (Supports 1M+ rows via Polars)
2. **Domain & Business Objective Inference** + **Automated Data Dictionary Generation**
3. **Statistical Data Quality Auditing** (Missing values, duplicates, IQR outliers, datatype mismatches, & 0–100 Health Score)
4. **AI-Planned & Vectorized Data Cleaning** (Imputation, deduplication, IQR capping, type casting, text standardization)
5. **Automated Exploratory Data Analysis (EDA)** (Univariate stats, correlation matrices, time-series trends, top/bottom segmentations)
6. **Zero-Copy SQL KPI Discovery & Execution** (Revenue, Profit, Cost, Customer, Order, and Retention metrics via DuckDB)
7. **Automated Visualization & Executive Dashboard Layout Design** (Plotly interactive charts)
8. **Quantified Business Insights, Multi-Dimensional Root Cause Analysis, & Hallucination Verification**
9. **7-Part Consulting Storytelling & Strategic/Tactical Recommendations**
10. **One-Click Export to Executive PDF (`ReportLab`), PowerPoint Deck (`python-pptx`), & Standalone HTML Dashboard**
11. **Conversational Data Chat (Natural Language -> DuckDB SQL -> Live Chart + Explanation)**

---

## 🧠 Architecture Philosophy: "Brain vs. Muscles"

Large Language Models are exceptional at semantic reasoning but slow and unreliable at arithmetic over large tables. This system strictly enforces a **Zero-Raw-Data-To-LLM** architecture:

* **🧠 Gemini API = The Brain (`core/llm.py`):**
  Handles domain understanding, cleaning strategy planning, SQL generation, chart selection, root-cause reasoning, insight verification, and executive storytelling. It **only** receives lightweight JSON metadata, schemas, and pre-computed statistical summaries.
* **💪 Python Data Stack = The Muscles (`analysis/`):**
  **Polars** and **DuckDB** execute all heavy file I/O, vectorized data cleaning, correlation matrices, aggregations, SQL queries, and chart/report rendering locally in milliseconds.

---

## 🤖 The 17-Agent Autonomous Ecosystem

Every agent inherits from `BaseAgent` (`agents/base.py`), enforcing structured Pydantic V2 inputs/outputs, execution telemetry (`AgentTrace`), and SHA-256 disk caching.

| # | Agent Name | File Path | Core Responsibility | Output Model |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Orchestrator Agent** | `agents/orchestrator_agent.py` | Coordinates the DAG pipeline, manages `PipelineContext`, and supports custom plugin agents. | `PipelineContext` |
| **2** | **File Agent** | `agents/file_agent.py` | Reads CSV/XLSX (multi-sheet), detects datatypes, and computes column distributions. | `DatasetProfile` |
| **3** | **Business Understanding Agent** | `agents/business_agent.py` | Infers industry domain, objectives, candidate KPIs, and builds the **Data Dictionary**. | `BusinessContext` |
| **4** | **Data Quality Agent** | `agents/data_quality_agent.py` | Audits nulls, duplicates, IQR outliers, and computes a weighted **0–100 Health Score**. | `DataQualityReport` |
| **5** | **Cleaning Planner Agent** | `agents/cleaning_planner_agent.py` | Synthesizes a deterministic JSON cleaning plan tailored to detected quality issues. | `CleaningPlan` |
| **6** | **Cleaning Executor Agent** | `agents/cleaning_executor_agent.py` | Executes imputation, deduplication, IQR clipping, and casting in Polars; re-audits health score. | `CleaningReport` |
| **7** | **EDA Agent** | `agents/eda_agent.py` | Computes univariate summaries, correlation pairs, time trends, and top/bottom segments. | `EDAReport` |
| **8** | **KPI Agent** | `agents/kpi_agent.py` | Generates read-only DuckDB SQL definitions for key business KPIs and computes exact values. | `KPIReport` |
| **9** | **Visualization Agent** | `agents/visualization_agent.py` | Maps analytical findings to optimal chart types (`line`, `bar`, `scatter`, `histogram`, `heatmap`, `treemap`). | `VisualizationReport` |
| **10** | **Dashboard Designer Agent** | `agents/dashboard_designer_agent.py` | Organizes KPIs and charts into a 3-tier executive grid layout. | `DashboardLayout` |
| **11** | **Insight Agent** | `agents/insight_agent.py` | Translates raw KPI ratios and statistical variances into quantified business insights. | `InsightReport` |
| **12** | **Root Cause Agent** | `agents/root_cause_agent.py` | Drills down across segments, categories, and correlations to rank primary root causes. | `RootCauseReport` |
| **13** | **Verification Agent** | `agents/verification_agent.py` | Secondary AI auditor that cross-checks insights against ground-truth math to prevent hallucinations. | `VerificationResult` |
| **14** | **Recommendation Agent** | `agents/recommendation_agent.py` | Formulates prioritized Strategic, Tactical, and Immediate Next Actions with expected impact. | `RecommendationReport` |
| **15** | **Storytelling Agent** | `agents/storytelling_agent.py` | Crafts a 7-part McKinsey/BCG-style executive narrative (*What, Why, Impact, Risks, Opportunities, Actions*). | `StorytellingReport` |
| **16** | **Report Agent** | `agents/report_agent.py` | Compiles downloadable **PDF**, **PowerPoint (`.pptx`)**, and **Interactive HTML** reports. | `PipelineArtifacts` |
| **17** | **SQL Chat Agent** | `agents/sql_chat_agent.py` | Powers conversational analytics: converts natural language questions into DuckDB SQL + live Plotly charts. | `NLQueryPlan` |

---

## ☁️ Deploying Live on Streamlit Community Cloud

This project is pre-configured for **1-click deployment on Streamlit Community Cloud** with built-in support for `st.secrets` and a built-in sample dataset checkbox for visitors.

### Step 1: Push Your Code to GitHub
Make sure your `.env` file is **not** committed (`.gitignore` already excludes `.env`).
```bash
git init
git add .
git commit -m "Initial commit: Autonomous AI Data Analyst"
git branch -M main
git remote add origin [https://github.com/jyoti-kushwaha01/ai-data-analyst.git](https://github.com/jyoti-kushwaha01/ai-data-analyst.git)
git push -u origin main
# Beastlife AI Automation & Customer Intelligence Prototype

This repository contains a complete prototype for the Beastlife customer care automation challenge.

The system ingests customer queries from multiple channels, classifies each query into issue categories, computes issue distribution percentages, tracks trends over time, and surfaces insights in a dashboard.

## What This Prototype Delivers

1. Automated query categorization (rule-based baseline + optional LLM fallback).
2. Problem distribution metrics (% of queries by issue type).
3. Weekly and monthly trend tracking.
4. Interactive dashboard for support and operations teams.
5. AI automation opportunities to reduce manual support workload.

## Repository Structure

- `docs/workflow.md` - End-to-end architecture diagram and automation design.
- `data/sample_queries.csv` - Sample multi-channel customer query dataset.
- `src/categorizer.py` - AI categorization logic.
- `src/analyze_queries.py` - Analytics pipeline to generate distributions and trends.
- `dashboard/app.py` - Streamlit dashboard app.
- `outputs/` - Generated outputs after running analysis.

## Category Taxonomy

The classifier maps each customer message into one of the following categories:

- Order status
- Delivery delay
- Refund request
- Product issue
- Subscription issue
- Payment failure
- General product question
- Other

## AI + Automation Workflow

Full workflow with diagram: `docs/workflow.md`

High-level flow:

1. Ingest messages from Instagram, WhatsApp, email, and web chat.
2. Normalize message payload.
3. Classify issue type using `src/categorizer.py`.
4. Route to automation:
	- Auto-reply / FAQ response for routine issues.
	- Human escalation for low confidence or sensitive queries.
5. Store classified events and generate analytics.
6. Visualize issue percentages and time trends in dashboard.

## Setup

```bash
pip install -r requirements.txt
```

## Run Analysis Pipeline

```bash
python src/analyze_queries.py
```

Optional LLM-assisted classification (if `OPENAI_API_KEY` is set):

```bash
python src/analyze_queries.py --use-llm
```

Generated files:

- `outputs/classified_queries.csv`
- `outputs/issue_distribution.csv`
- `outputs/weekly_trends.csv`
- `outputs/monthly_trends.csv`
- `outputs/automation_opportunities.csv`
- `outputs/summary.json`

## Launch Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard shows:

1. Percentage of total queries by issue category.
2. Most common customer problems.
3. Weekly/monthly trend lines by issue type.
4. Channel mix (Instagram, WhatsApp, Email, Web chat).
5. Recommended AI automation opportunities prioritized by issue volume.

## Current Sample Output

From `outputs/issue_distribution.csv`:

| Issue Type | % of Queries |
|---|---:|
| Order status | 35.0% |
| Delivery delay | 22.5% |
| Refund request | 17.5% |
| Product issue | 15.0% |
| Subscription issue | 5.0% |
| Payment failure | 2.5% |
| General product question | 2.5% |

## Automation Opportunities by Issue

1. Order status
	- Auto-fetch tracking from OMS and send ETA instantly.
2. Delivery delay
	- Trigger delay apology, revised ETA, and goodwill coupon if SLA breached.
3. Refund request
	- Validate policy and auto-create refund ticket with required details.
4. Product issue
	- Collect evidence (SKU/batch/photos), then route to QA + replacement flow.
5. Subscription issue
	- Self-serve pause/skip/cancel links.
6. Payment failure
	- Smart retry prompts with alternate payment methods.
7. General questions
	- AI FAQ assistant powered by knowledge base retrieval.

## Scalability Design

1. Message queue between ingestion and classifier for burst handling.
2. Stateless classifier workers with horizontal autoscaling.
3. Event store + scheduled aggregation jobs (5-15 minute cadence).
4. Confidence-based human-in-the-loop fallback to maintain quality.
5. Continuous learning loop from corrected agent labels.

## Suggested Production Stack

- AI: OpenAI API (or equivalent LLM provider)
- Orchestration: n8n / Zapier / Make
- Backend services: Python (FastAPI workers)
- Data/analytics: PostgreSQL + dbt + BI dashboard (Looker Studio / Power BI)
- Monitoring: SLA dashboards + alerting (Datadog/Grafana)

## Why This Meets the Assignment Criteria

1. Practical AI-powered workflow for customer support automation.
2. Clear categorization engine and explainable taxonomy.
3. Actionable insight extraction via percentages and trend analysis.
4. Dashboard to monitor top issues and query patterns.
5. Scalable architecture for higher query volumes.

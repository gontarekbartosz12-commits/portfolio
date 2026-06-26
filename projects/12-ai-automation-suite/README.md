# AI Automation Suite (n8n)

Six production-grade n8n automations that demonstrate the core patterns of modern AI Automation / Agent Engineering: multi-agent orchestration, RAG, LLM-as-judge evaluation, human-in-the-loop approval, structured outputs, document AI, and scheduled ingestion. Every workflow JSON in this folder is importable into n8n.

## Workflows

### 01 - Multi-Agent Research & Report Writer (`01-multi-agent-research.json`)
Enter a topic via a form and receive a researched report by email. A Planner agent splits the topic into focused sub-questions (structured output), a Researcher agent investigates each one, a Synthesizer writes a Markdown report, a Critic agent scores it and lists missing angles (structured output), and a Reviser produces the final polished version. Showcases multi-agent orchestration, fan-out/fan-in over sub-questions, structured outputs, and a self-critique/revision loop.

### 02 - Customer Support AI Agent — RAG + HITL (`02-support-ai-rag-hitl.json`)
An inbound support ticket (webhook) is triaged by category, urgency and sentiment, then answered using self-contained RAG over a policy knowledge base (in-memory vector store + OpenAI embeddings). An LLM-as-judge scores the draft for faithfulness and confidence: high-confidence replies auto-send, low-confidence ones route to a human approval email before sending. Showcases RAG, grounded generation, LLM-as-judge evaluation, and human-in-the-loop routing.

### 03 - AI Document / Invoice Processing (`03-ai-invoice-processing.json`)
Upload a PDF invoice through a form. The workflow extracts text (with an empty-text fallback that flags scanned images for manual OCR), uses an AI agent with a structured-output schema to extract vendor, totals, dates and line items, runs validation and anomaly checks (subtotal+tax vs total, high-value threshold), then auto-files clean invoices to an n8n Data Table while routing flagged ones to a human approval email. Showcases document AI, structured extraction, deterministic validation, and human-in-the-loop.

### 04 - Content Repurposing Machine (`04-content-repurposing.json`)
Paste any long-form content and get a full multi-platform content pack by email. An Extract Core agent distills a headline, key points and hooks (structured output); a Repurpose agent generates a Twitter/X thread, a LinkedIn post, an Instagram caption, a YouTube description and a newsletter section, all matched to a chosen brand voice. Showcases structured fan-out generation and brand-consistent copywriting.

### 05 - Smart Inbox Triage & Auto-Draft (`05-inbox-triage-autodraft.json`)
A new (unread) email triggers AI classification of category, priority, needs-reply and a one-line summary (structured output). If a reply is warranted, an AI agent drafts it and saves a Gmail draft in the same thread for the user to review and send. Safe by design — it never auto-sends. Showcases triage, structured outputs, and assistive (not autonomous) drafting.

### 06 - Daily AI & Tech News Digest (`06-daily-ai-news-digest.json`)
Every morning a schedule trigger fetches front-page tech stories from Hacker News (no API key), an AI curator picks the five most relevant for an AI-first builder with a one-line "why it matters" each (structured output), and the result is formatted as HTML and emailed. Showcases scheduling, API ingestion, structured curation, and reporting.

## How to import

1. In n8n, open **Workflows → Import from File** and select any `*.json` from this folder.
2. Open each credential-bound node (OpenAI chat/embeddings, Gmail) and connect **your own** OpenAI and Gmail credentials — credentials are referenced by name only, never included.
3. In the email-sending nodes, set the recipient field (currently `you@example.com`) to your address. For workflow 03, point the Data Table nodes at your own table (placeholder `YOUR_DATA_TABLE_ID`).
4. Activate the trigger (form, webhook, Gmail or schedule) as needed.

All six were built with the n8n Workflow SDK and tested live on an n8n Cloud instance.

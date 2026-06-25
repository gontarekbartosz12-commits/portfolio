# n8n Automation Workflows — low-code agentic pipelines

A suite of **n8n** workflows I built and tested end-to-end — from production **AI agents,
an autonomous lead pipeline and a RAG assistant with evaluation**, to trading research /
execution and lead generation. They combine AI Agents, structured outputs, RAG, HTTP/REST
APIs, custom code nodes, branching logic and persistence.

> All workflows are **sanitised**: credentials are placeholders or referenced by name,
> never included. Trading flows ship with `dry_run: true`.

## ⭐ Featured (2026): production AI agents, an autonomous pipeline & RAG

Four AI automations built and tested live with **Claude Code + the n8n MCP**. Dedicated
repo with README + architecture diagram:
**https://github.com/gontarekbartosz12-commits/n8n-ai-automation-portfolio** — all
exported here as importable JSON.

- **`01-chatbot-salon-fryzjerski.json` — Booking chatbot.** OpenAI agent with tool-calling
  + conversation memory, integrated with Google Calendar (checks availability, books the
  appointment). Embeddable web widget.
- **`02-sekretarka-glosowa-elevenlabs.json` — Voice-agent backend.** Webhook for an
  ElevenLabs voice agent → validates/normalises data → Google Calendar availability +
  booking → structured reply.
- **`03-ai-lead-engine.json` — Autonomous lead pipeline.** Webhook → LLM with **structured
  JSON output** (lead scoring 0–100, intent, category) → conditional routing → CRM (n8n
  Data Table) + auto-generated personalized email. *Tested live: hot lead scored 85/100,
  CRM row written, both emails sent in ~22 s.*
- **`04-rag-eval-asystent-wiedzy.json` — RAG with evaluation.** OpenAI embeddings →
  in-memory vector store → top-k retrieval → grounded answer → **LLM-as-judge** scoring
  faithfulness / relevance / hallucination-risk (structured output). *Tested live: top
  chunk cosine 0.74, faithfulness 1.0.*

### What these demonstrate
AI Agents (tool-calling, memory), **structured outputs**, decision routing, **RAG
(embeddings + retrieval + grounding)**, **LLM evaluation** (faithfulness / hallucination),
webhooks/APIs, data persistence and multi-channel side-effects.

## Also: Kalshi Micro-Agent v4 (agentic trading)
An end-to-end **agentic trading pipeline** on the Kalshi prediction market — 20+ nodes:

```
⏰ Schedule (30 min) / ▶️ Manual
   → ⚙️ Config (keys, dry_run)
   → 🔐 RSA-sign per series (crypto, RSA-PSS SHA-256)
   → 📊 Fetch ~50 Kalshi series (batched HTTP, auth headers)
   → 🔀 Merge + sign balance/positions
   → 💰 Balance  → 📦 Positions
   → 🔄 Filter markets (price band, time-to-close, liquidity, dedup)
   → ⚖️ Ready?  ──no──► ⛔ Stop
        │yes
   → 🧠 Build prompt  → 🤖 Claude analysis (Anthropic API)
   → 📈 Parse & decide (edge ≥10pp, risk caps: ≤2 contracts, ≤50c/trade)
   → 🚀 Execute?  ──no──► 📋 Log scan (Google Sheets)
        │yes
   → 🔐 Sign order  → 💰 Place order (Kalshi)  → 📋 Log trade (Google Sheets)
```

### What it demonstrates (n8n skills)
- **Custom code nodes** — request signing with Node `crypto` (RSA-PSS / SHA-256), JSON
  parsing, validation and risk rules written in JavaScript inside n8n.
- **HTTP Request nodes** — authenticated REST calls with dynamic headers, batching and
  `neverError` handling.
- **LLM integration** — calls the Anthropic API and parses the model's JSON decision.
- **Control flow** — `IF` branching, `Merge`, schedule + manual triggers, safe `dry_run`.
- **Persistence** — append-only **Google Sheets** logging for every scan and trade.

## Other workflows in the suite (described, not all exported here)
- **Kalshi multi-stage** — `stage1-scanner` + `stage2-executor` split for separation of concerns; RSA and HTTP-node variants.
- **AI Trading Agent L2** — mean-reversion + sentiment; schedule → HTTP data → code signals → LLM → Sheets.
- **Crypto Scalping Agent (24/7)** — momentum scalping loop on exchange APIs.
- **Voltex Lead Scraper** *(included: `voltex-lead-scraper.json`)* — lead-generation automation: SerpAPI Google-Maps search → parse business leads → store. A non-trading example showing breadth. *(Sanitised — SerpAPI key is a `WKLEJ_SERPAPI_KEY` placeholder.)*

## What it shows an employer
I can design and ship **real low-code/agentic automations** end-to-end in n8n — not toy
demos: scheduling, authenticated APIs, cryptographic signing, LLM-in-the-loop decisions,
guardrails and logging.

## Stack
n8n · JavaScript (code nodes, Node crypto) · REST/HTTP · Anthropic API · Google Sheets · cron/schedule

# n8n Automation Workflows — low-code agentic pipelines

A suite of **n8n** workflows I built to automate trading research, execution and lead
generation — combining HTTP APIs, custom code nodes, branching logic, an LLM
decision step and Google Sheets logging.

> The included `kalshi-micro-agent-v4.json` is **sanitised**: all credentials are
> placeholders (`TUTAJ_KEY_ID`, `TUTAJ_KLUCZ_PEM`, `TUTAJ_CLAUDE_KEY`) and it ships with
> `dry_run: true`. No real keys.

## ⭐ Showcase: Kalshi Micro-Agent v4 (multi-series)
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
- **Voltex Lead Scraper / Master** — lead-generation automation (scrape → enrich → store) for an electrical-works brand.

## What it shows an employer
I can design and ship **real low-code/agentic automations** end-to-end in n8n — not toy
demos: scheduling, authenticated APIs, cryptographic signing, LLM-in-the-loop decisions,
guardrails and logging.

## Stack
n8n · JavaScript (code nodes, Node crypto) · REST/HTTP · Anthropic API · Google Sheets · cron/schedule

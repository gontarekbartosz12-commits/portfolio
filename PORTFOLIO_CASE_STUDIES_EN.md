# Bartosz Gontarek — Project Portfolio
### Selected builds · 2025–2026 · AI-first development

> Everything below was designed and built by me using an AI-first workflow
> (Claude Code, Cursor, Gemini) with Model Context Protocol (MCP) to connect
> agents to live data. Code samples in this portfolio are **sanitised** — all
> API keys and secrets are removed and replaced with environment variables.

> **Positioning:** my core priority is **AI & automation engineering** (projects 1–10 below — all active works-in-progress). **Branded e-commerce** (final section) is an **additional income stream** I run in parallel, not my main focus.

---

## 1. Polymarket Trading Bots — algorithmic prediction-market systems
**Stack:** Python · Polymarket Gamma & CLOB API · Polygon/Web3 (`py-clob-client`) · Simmer API · REST · Linux VPS + cron · Telegram alerts

### The problem
Prediction markets (Polymarket) misprice fast-moving events. I wanted to find out, with real code and real data, **whether a retail-sized account can extract an edge** — and which strategies actually survive contact with the market.

### What I built
A family of cooperating Python bots, each isolating one hypothesis:

1. **Copy-trader** — tracks top on-chain wallets (e.g. "ColdMath"), detects *new* positions via the Polymarket data API, and mirrors them at a fixed % of balance with per-market exposure caps.
2. **AI-divergence scanner** — pulls an independent AI fair-value estimate per market and trades only when it diverges from the live market price by ≥10 percentage points.
3. **BeastBot view-count model** — a quantitative model for YouTube-views markets (see project #2).
4. **Limitless LP bot** — automated liquidity provision / inventory management on the Limitless protocol (Base chain) with its own backtester and monitor.

### How it works (engineering)
- **Position diffing:** keeps a `KNOWN_POSITIONS` snapshot per wallet and emits a trade only on the *delta* (new position appears) — avoids re-copying stale holdings.
- **Risk layer:** every bot enforces `COPY_PCT`, `MIN_POSITION_VALUE`, `MAX_TRADE_SIZE`, max daily trades and a drawdown cap before any order is placed.
- **Resilience:** all network calls are wrapped with timeouts + try/except and the main loop self-heals (`sleep` + retry) so a flaky API never kills the process.
- **Deployment:** runs headless on a Linux VPS under cron; sends fills and errors to Telegram.

### Outcome & honest result
Run in **virtual ($SIM) / paper mode first**. The most valuable result was *negative*: by auditing **~3,380 on-chain trades** of a "guru" wallet I proved that naïve copy-trading is **mathematically unprofitable at retail scale** (fees + slippage + adverse selection ≈ −$222/week on a $300 stake). That killed a bad strategy *before* risking real money — and pushed the project toward model-driven edges (divergence, view-count curves) instead.

### What it demonstrates
Real API integration, Web3 basics, risk management, data-driven decision making, and the discipline to **falsify my own ideas with evidence** rather than chase a story.

---

## 2. BeastBot — quant model for YouTube-views markets
**Stack:** Python 3.10+ · SciPy (sigmoid curve fitting) · YouTube Data API v3 · Polymarket Gamma API · Normal-CDF pricing · multi-agent consensus ("Hermes")

### The edge
Markets ask "will video X reach N views by date D?". Early view data (T+6h…T+24h) follows a **sigmoid growth curve**. I fit that curve to project the saturation view count, convert it to a bucket probability with a Normal CDF, and trade only when the market's implied probability **diverges from my model by ≥8 pp**.

### Architecture (clean, modular)
```
sources/   → live views (YouTube API) + scraper fallback
model/     → growth_curves (sigmoid fit) · historical baseline · bootstrap CI
hermes/    → 3 agents (live API / curve / historical) → weighted consensus
pricer.py  → Normal CDF → bucket probabilities
trader.py  → main loop · monitor.py → exit logic
```
- **Calibrated uncertainty:** `SIGMA_BY_HORIZON` widens the confidence band for longer horizons (grounded in Szabó & Huberman's view-growth literature).
- **Consensus scoring:** a "Hermes" aggregator blends three signals with explicit weights and skips any market below `medium` confidence.
- **Secrets done right:** all keys via `os.getenv()` — nothing hardcoded.
- **Exit rules:** sells at residual edge <2 pp, −15% stop-loss, or when the edge decays below 3% while profitable.

### What it demonstrates
Applied statistics/ML (curve fitting, calibrated probabilities), clean modular architecture, and turning a research idea into a deployable, risk-bounded system.

---

## 3. "Mrok Otchłani" — single-file HTML5/Canvas ARPG  *(in progress)*
**Stack:** JavaScript (ES6) · HTML5 Canvas · **zero dependencies, zero build step**

### What it is
A top-down, Diablo-like action-RPG that runs from a single HTML file. WASD movement + mouse aim, procedurally generated pixel-art, and a **paper-doll system** where equipped gear actually changes the character's on-screen appearance.

### Engineering highlights
- **Procedural pixel-art:** sprites and environment tiles generated in code rather than shipped as image assets — the whole game is self-contained.
- **Game loop:** `requestAnimationFrame` render/update split, entity system for enemies/loot/projectiles, collision and simple AI.
- **Paper-doll rendering:** equipment layers composited over the base character at draw time.
- Shipped **v0.1, reviewed with 0 blocker bugs**; roadmap to v0.4. A v2 rebuild is in progress.

### What it demonstrates
Strong vanilla-JS fundamentals, real-time rendering, state management and game-systems design — without leaning on a framework.

---

## 4. STRONEVO — web-studio brand & demo system  🌐 *LIVE at [stronevo.pl](https://stronevo.pl)*
**Stack:** HTML/CSS/JS · responsive design · branding/identity

### What it is
My own web-design studio brand. I built a **catalog site** plus **three "offline-proof" demo websites** — self-contained client mock-ups that load and render without a backend, so prospects can click through a real-feeling site before committing.

### What I did
- Defined the brand (name, visual identity, positioning).
- Built the catalog/portfolio front-end and the demo sites (responsive, fast, dependency-light).
- Packaged everything as a deployable `dist/` ready for hosting + a custom domain.

### What it demonstrates
Front-end delivery end-to-end, design sensibility, and the ability to productise a service — useful for any consumer-facing product team.

---

## 5. AI Agents & Voice — autonomous assistants and pipelines
**Stack:** Python · Telegram Bot API · cron/VPS · Google Trends + Amazon scraping · Hume Octave (voice synthesis) · MCP

### What it is
A set of **always-on autonomous agents** I run on my VPS, plus voice-enabled AI work:
- **"Świstak" (Telegram assistant/notifier)** — the human-facing channel for all my bots: pushes trade fills, daily reports and alerts; receives commands.
- **trends_scout** — a daily agent (06:00 UTC) that scans foreign product/market trends (Google Trends + Amazon) and writes a digest to Telegram and my Obsidian knowledge vault. Runs at $0/month.
- **Voice synthesis** — built character voices with **Hume Octave 2** for the Mia Vex persona (project #6); explored TTS pipelines for conversational agents.
- **MCP integrations** — wired tools like the official **Alpaca MCP** (stock trading) and image-gen MCPs into agentic workflows, so an AI agent can call live trading/data tools directly.

### How it works
- Each agent is a self-contained Python service scheduled by cron, with environment-based secrets and Telegram as the unified I/O layer.
- Failures are caught and reported, not silently dropped; state persists to JSON/vault between runs.

### What it demonstrates
Exactly the "agentic workflows + MCP" skill set this role asks for — turning LLMs into tools that *act* (schedule, fetch, decide, notify) rather than just chat.

---

## 6. Mia Vex — end-to-end AI persona & content pipeline  *(in progress)*
**Stack:** Gemini 3 Pro Image / Vertex AI · ComfyUI · RunPod (cloud GPU) · LoRA training · Hume voice · prompt engineering

### What it is
A complete, reproducible pipeline for generating a consistent AI character across images and voice — from a locked persona definition to publish-ready assets.

### What I did
- Set up **Vertex AI / Gemini image generation** (service account, GCP project, org-policy and key configuration) and validated end-to-end generation.
- Designed the **production pipeline**: Z-Image/LoRA character consistency on RunPod GPUs → image generation → a 4-step publication-hygiene process (consistency, detailing, upscaling, metadata).
- Synthesised **110+ research sources** (91 videos + a full course) into a single A-to-Z operating "compendium" so the workflow is repeatable by anyone.
- Selected **Hume Octave 2** for free, high-quality voice.

### What it demonstrates
Cloud GPU orchestration, generative-AI tooling beyond chat, rigorous research-to-system synthesis, and shipping a real multi-stage pipeline.

---

## 7. Video Transcriber — autonomous speech-to-text service
**Stack:** Python 3.12 · OpenAI Whisper · CUDA/GPU (RTX) · `uv` · Windows auto-start watcher

### What it is
A hands-off transcriber: drop a video in a folder and it produces subtitles automatically. Prefers existing captions, falls back to **Whisper** speech-to-text on the GPU, and writes results into my Obsidian vault.

### Engineering highlights
- **Folder-watcher** auto-starts at login and processes new files with no manual step.
- GPU-accelerated inference (RTX), reproducible Python env via `uv`, model size tuned per language (small / medium for Polish).

### What it demonstrates
Practical ML deployment (running real ASR models locally on GPU), automation, and environment/repro discipline.

---

## 8. n8n Automation Workflows
**Stack:** n8n · JavaScript code nodes (Node crypto) · REST/HTTP · Anthropic API · Google Sheets · schedule

A suite of **low-code agentic pipelines** built in n8n. The showcase is a **Kalshi micro-trading agent** (20+ nodes): schedule → RSA-sign requests (crypto) → fetch ~50 market series → filter → **Claude API analysis** → risk-checked decision → signed order → Google Sheets logging, with a safe `dry_run` switch.

- **Custom code nodes** — RSA-PSS / SHA-256 request signing, JSON parsing, validation and risk rules in JS.
- **LLM-in-the-loop** — calls the Anthropic API and parses the model's JSON trade decision.
- **Control flow** — IF branching, Merge, schedule + manual triggers, append-only Sheets logging.
- Plus: Kalshi multi-stage scanner/executor, a crypto scalping agent, and a Voltex lead-scraper.

**Demonstrates:** real low-code/automation delivery — scheduling, authenticated APIs, cryptographic signing, LLM decisions and guardrails. *(Included workflow is sanitised — placeholder keys, dry-run on.)*

---

## 9. Alpaca Stock Trader — Lumibot bot + Alpaca MCP
**Stack:** Python · Lumibot · Alpaca API (paper) · Model Context Protocol · systemd · pytest

An automated **US-equities paper-trading bot** on Alpaca, plus an AI variant where an LLM places trades through the **official Alpaca MCP** server — productionised, not a notebook.

- **Strategy** — ConservativeV1: RSI + Bollinger Bands + SMA50/200 trend filter, with pure-logic unit tests.
- **Ops** — systemd service (resource limits + hardening), idempotent 8-phase deploy, post-deploy smoke test (auth, orders, positions, Telegram).
- **MCP integration** — Claude queries the account and places orders via Alpaca MCP tools; paper-first.

**Demonstrates:** productionised trading infra + the exact agentic/MCP skill the role asks for, on a real broker API. *(Paper-only; secrets env-based.)*

---

## 10. Tradebot — swing-momentum backtest
**Stack:** Python · vectorbt · pandas · yfinance · Jupyter

A rigorous backtest built to decide **whether a production bot was worth building** — with explicit gates that said "not yet". That disciplined "no" is the point.

- **Method** — composite momentum + ADX/SMA trend filter, no-look-ahead entries, ATR trailing stops, 5 bps slippage, **walk-forward validation** (6 folds).
- **Decision gates** — Sharpe ≥ 0.5, max DD ≤ 15%, walk-forward Sharpe ≥ 0.3, ≥ 150 trades — fail any → don't ship.
- **Honesty** — openly documents survivorship + look-ahead biases and mitigations.

**Demonstrates:** quant rigor and evidence-gated decisions — the maturity to *not* ship a losing strategy.

---

## ★ Websites & Branded E-commerce — additional income stream
**Stack:** WordPress · WooCommerce · Shopify · NextCart/Takedrop · payments (P24/PayU) · InPost/logistics · branding

Alongside my AI work, I design and ship **branded online stores end-to-end** — the whole funnel: product pages and copy, payment + shipping integrations, legal pages and the brand identity. This is an **additional, parallel income stream** — it funds the AI building, which is my main focus.

### Builds
- **STRONEVO** — my web-studio brand, **live at [stronevo.pl](https://stronevo.pl)** + offline-proof demo sites to win clients *(active)*.
- **Balustrady (client website)** — full WordPress build pack for a railings company: 10-page site, mega-menu, product template, filtered gallery, quote form, unique SEO + schema per page, GA4/Pixel tracking *(built, ready to deploy)*.
- **Amovo** — dropshipping store on NextCart/Takedrop (FreshSwap line): product cards, policies, InPost + home delivery *(active)*.
- **Lokse** — single-product WooCommerce store (fingerprint padlock), custom brand.
- **GhostShell** — *former brand* (anti-peep phone cases), no longer active.

**Demonstrates:** end-to-end product delivery, conversion and the full commerce stack (payments, logistics, compliance), and brand sensibility.

---

## How I work
- **AI-first by default:** Claude Code + Cursor + Gemini as my IDE; MCP to give agents real tools; subagents for parallel work.
- **Ship, then prove it:** every trading idea is paper-tested and audited against real data before a cent is risked.
- **Secrets & safety:** environment variables, never hardcoded keys; I rotate anything exposed.
- **Self-documenting:** projects carry READMEs, risk limits, and an Obsidian knowledge base.

**Certified (2026) — 11 certificates:** *Anthropic* — Claude Code in Action · MCP: Advanced Topics · Introduction to MCP · AI Fluency (Framework & Foundations, students, educators, nonprofits, Teaching the Framework). *IBM SkillsBuild* — AI Literacy · AI Fundamentals (Foundations · Language & Vision).

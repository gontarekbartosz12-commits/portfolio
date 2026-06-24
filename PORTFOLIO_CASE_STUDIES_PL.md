# Bartosz Gontarek — Portfolio projektów
### Wybrane realizacje · 2025–2026 · praca AI-first

🔗 **GitHub:** https://github.com/gontarekbartosz12-commits/portfolio

> Wszystko poniżej zaprojektowałem i zbudowałem samodzielnie w podejściu AI-first
> (Claude Code, Cursor, Gemini), z użyciem Model Context Protocol (MCP) do podłączania
> agentów do danych na żywo. Fragmenty kodu są **oczyszczone** — wszystkie klucze API i
> sekrety usunięte i zastąpione zmiennymi środowiskowymi.

> **Pozycjonowanie:** moim głównym priorytetem jest **inżynieria AI i automatyzacji** (projekty 1–10 — wszystkie aktywne, w toku). **Branded e-commerce** (ostatnia sekcja) to **dodatkowe źródło dochodu**, które prowadzę równolegle, nie główny fokus.

---

## 1. Boty tradingowe Polymarket — algorytmiczne systemy na rynkach predykcyjnych
**Stack:** Python · Polymarket Gamma & CLOB API · Polygon/Web3 · Simmer API · Linux VPS + cron · Telegram

**Problem:** rynki predykcyjne źle wyceniają szybkie wydarzenia. Chciałem sprawdzić realnym kodem, czy konto detaliczne ma przewagę i które strategie przetrwają.
**Co zbudowałem:** copy-trader (kopiuje *nowe* pozycje czołowych portfeli on-chain), skaner dywergencji AI (handel przy ≥10 pp rozjazdu), model wyświetleń BeastBot, bot LP Limitless (Base, z backtesterem).
**Inżynieria:** diffowanie pozycji (tylko delta), warstwa ryzyka (limity przed każdym zleceniem), odporność (timeouty + samoleczenie pętli).
**Uczciwy wynik:** tryb paper/$SIM. Audyt **~3 380 transakcji on-chain** udowodnił, że naiwny copy-trading jest nieopłacalny na skalę detaliczną (≈ −222 $/tydz. przy 300 $) — zabiło złą strategię przed ryzykiem realnego kapitału.
**Pokazuje:** integracje API + Web3, zarządzanie ryzykiem, falsyfikowanie własnych pomysłów danymi.

## 2. BeastBot — model ilościowy rynków wyświetleń YouTube
**Stack:** Python 3.10+ · SciPy · YouTube Data API · Polymarket Gamma · wycena rozkładem normalnym · konsensus agentów

Wczesne dane o wyświetleniach układają się w **krzywą sigmoidalną** → projekcja wysycenia → prawdopodobieństwo bucketu → handel przy ≥8 pp rozjazdu z rynkiem. Skalibrowana niepewność, konsensus „Hermes" z jawnymi wagami, sekrety przez `os.getenv()`.
**Pokazuje:** stosowaną statystykę/ML, czystą architekturę modułową, research → wdrażalny system z ograniczeniem ryzyka.

## 3. „Mrok Otchłani" — ARPG w HTML5/Canvas  *(w toku)*
**Stack:** JavaScript (ES6) · HTML5 Canvas · zero zależności

Top-down Diablo-like z jednego pliku HTML: WASD + mysz, **proceduralny pixel-art**, system **paper-doll** (ekwipunek zmienia wygląd). Pętla na requestAnimationFrame, system encji, kolizje. Wydane v0.1 (0 blokerów), trwa v2.
**Pokazuje:** mocne podstawy vanilla-JS, rendering real-time, projektowanie systemów gry bez frameworka.

## 4. STRONEVO — marka studia WWW i system dem  🌐 *LIVE: [stronevo.pl](https://stronevo.pl)*
**Stack:** HTML/CSS/JS · responsywność · branding

Wdrożone i działa na **stronevo.pl** („Strony internetowe i sklepy — Warszawa, Piaseczno"). Strona-katalog + 3 „offline-proof" strony demo (renderują się bez backendu). Zdefiniowanie marki, build jako gotowy `dist/`.
**Pokazuje:** dowożenie front-endu end-to-end, wyczucie designu, uproduktowienie usługi.

## 5. Agenci AI i głos — autonomiczni asystenci
**Stack:** Python · Telegram Bot API · cron/VPS · Google Trends + Amazon · Hume Octave (głos) · MCP

- **„Świstak" (Telegram)** — wspólny kanał wszystkich botów: egzekucje, raporty, alerty, komendy.
- **trends_scout** — codzienny agent (06:00 UTC) skanujący zagraniczne trendy → Telegram + vault, 0 zł/mc.
- **Głos** — Hume Octave 2; eksploracja pipeline'ów TTS.
- **Integracje MCP** — oficjalny Alpaca MCP i MCP do obrazów w workflowach agentowych.

**Pokazuje:** dokładnie „workflowy agentowe + MCP" — LLM-y, które *działają*, nie tylko rozmawiają.

## 6. Mia Vex — pipeline persony i contentu AI  *(w toku)*
**Stack:** Gemini 3 Pro Image / Vertex AI · ComfyUI · RunPod · LoRA · głos Hume

Kompletny, powtarzalny pipeline spójnej postaci AI (obraz + głos). Konfiguracja Vertex/Gemini (GCP, service account, org policy), spójność LoRA na GPU RunPod, 4-stopniowa higiena publikacji, synteza 110+ źródeł w kompendium A-Z.
**Pokazuje:** orkiestrację GPU w chmurze, generatywną AI poza czatem, rygor research → system.

## 7. Video Transcriber — autonomiczne speech-to-text
**Stack:** Python 3.12 · OpenAI Whisper · CUDA/GPU (RTX) · uv · watcher na Windows

Wrzuć wideo → napisy automatycznie. Najpierw istniejące napisy, potem **Whisper** na GPU, wynik do Obsidian. Watcher przy logowaniu, powtarzalne środowisko `uv`.
**Pokazuje:** praktyczne wdrożenie ML (realny ASR na GPU), automatyzację, powtarzalność.

## 8. Workflowy automatyzacji n8n
**Stack:** n8n · JavaScript (code nodes, Node crypto) · REST/HTTP · Anthropic API · Google Sheets · schedule

Zestaw **low-code'owych pipeline'ów agentowych**. Flagowy: **agent micro-trading Kalshi** (20+ węzłów): schedule → podpis RSA (crypto) → ~50 serii rynków → filtr → **analiza Claude API** → decyzja z ryzykiem → podpisane zlecenie → log Google Sheets, z `dry_run`.
- **Własne code nodes** — podpisy RSA-PSS/SHA-256, parsowanie, walidacja, reguły ryzyka w JS.
- **LLM-in-the-loop** — wywołanie Anthropic API i parsowanie decyzji JSON.
- **Sterowanie** — IF, Merge, triggery, append-only log do Sheets.
- Plus: scanner/executor Kalshi, scalping crypto, scraper leadów Voltex.

**Pokazuje:** realne dowożenie automatyzacji low-code — harmonogramy, uwierzytelnione API, kryptografia, decyzje LLM, zabezpieczenia. *(Załączony workflow oczyszczony — placeholdery, dry-run on.)*

## 9. Alpaca Stock Trader — bot Lumibot + Alpaca MCP
**Stack:** Python · Lumibot · Alpaca API (paper) · Model Context Protocol · systemd · pytest

Automatyczny **bot paper-trading akcji USA** na Alpaca + wariant AI z **oficjalnym Alpaca MCP** (LLM składa zlecenia). Uproduktowiony, nie notebook.
- **Strategia** — ConservativeV1: RSI + Bollinger + filtr SMA50/200, testy jednostkowe logiki.
- **Ops** — usługa systemd (limity + hardening), idempotentny deploy, smoke-test po wdrożeniu.
- **MCP** — Claude odpytuje konto i składa zlecenia przez Alpaca MCP; paper-first.

**Pokazuje:** uproduktowioną infrastrukturę tradingową + umiejętność agentic/MCP na realnym API brokera. *(Tylko paper; sekrety w env.)*

## 10. Tradebot — backtest swing-momentum
**Stack:** Python · vectorbt · pandas · yfinance · Jupyter

Rygorystyczny backtest, by zdecydować, **czy warto budować bota produkcyjnego** — z jawnymi bramkami, które powiedziały „jeszcze nie".
- **Metoda** — momentum kompozytowe + filtr ADX/SMA, wejścia bez look-ahead, trailing stop ATR, walk-forward (6 foldów).
- **Bramki** — Sharpe ≥ 0,5, max DD ≤ 15%, walk-forward Sharpe ≥ 0,3, ≥ 150 transakcji.
- **Uczciwość** — otwarcie dokumentuje biasy survivorship/look-ahead.

**Pokazuje:** quant-rygor i decyzje oparte na dowodach — dojrzałość, by *nie* wdrożyć stratnej strategii.

## ★ Strony i branded e-commerce — dodatkowe źródło dochodu
**Stack:** WordPress · WooCommerce · Shopify · NextCart/Takedrop · płatności (P24/PayU) · InPost · branding

Obok pracy nad AI dowożę **brandowane sklepy online end-to-end** — cały lejek: karty produktów i copy, płatności i wysyłka, strony prawne, identyfikacja wizualna. To **dodatkowy, równoległy dochód** — finansuje budowanie AI, które jest moim głównym fokusem.

### Realizacje
- **STRONEVO** — moja marka studia WWW, **live na [stronevo.pl](https://stronevo.pl)** + offline-proof dema *(aktywne)*.
- **Balustrady (strona klienta)** — pełny build WordPress: 10 podstron, mega-menu, szablon produktowy, galeria, formularz wyceny, SEO + schema, GA4/Pixel *(zbudowane, gotowe do wdrożenia)*.
- **Amovo** — dropshipping na NextCart/Takedrop (FreshSwap): karty, regulaminy, InPost + dostawa *(aktywne)*.
- **Lokse** — jednoproduktowy sklep WooCommerce (kłódka na odcisk palca), własny branding.
- **GhostShell** — *była marka* (etui anti-peep), już nieaktywna.

**Pokazuje:** dowożenie produktu end-to-end, konwersję i pełny stack e-commerce, wyczucie marki.

---

## Jak pracuję
- **AI-first domyślnie:** Claude Code + Cursor + Gemini + MCP + sub-agenci.
- **Najpierw dowieź, potem udowodnij:** paper-test i audyt przed ryzykowaniem pieniędzy.
- **Sekrety i bezpieczeństwo:** zmienne środowiskowe, nigdy klucze na sztywno; rotuję cokolwiek się odsłoni.
- **Samodokumentacja:** README, limity ryzyka, baza wiedzy w Obsidian.

**Certyfikaty (2026) — 11:** *Anthropic* — Claude Code in Action · MCP: Advanced Topics · Introduction to MCP · AI Fluency (×5). *IBM SkillsBuild* — AI Literacy · AI Fundamentals (Foundations · Language & Vision).

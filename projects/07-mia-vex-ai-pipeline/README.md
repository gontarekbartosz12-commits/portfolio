# Mia Vex — end-to-end AI persona & content pipeline

A complete, reproducible pipeline for generating a **consistent AI character**
across images and voice — from a locked persona definition to publish-ready assets.

## What I built
- **Cloud generation setup** — Vertex AI / Gemini 3 Pro Image (GCP project, service
  account, org-policy and key configuration), validated end-to-end.
- **Production pipeline** — LoRA character-consistency on **RunPod** cloud GPUs →
  image generation → a 4-step publication-hygiene process (consistency → detailing →
  upscale → metadata).
- **Voice** — selected **Hume Octave 2** for high-quality, free synthesis.
- **Research synthesis** — distilled 110+ sources (91 videos + a full course) into a
  single A-to-Z operating "compendium" so the workflow is repeatable by anyone.

## What it demonstrates
Cloud GPU orchestration, generative-AI tooling beyond chat, prompt engineering, and
rigorous research-to-system synthesis.

## Stack
Gemini 3 Pro Image / Vertex AI · ComfyUI · RunPod · LoRA · Hume voice · prompt engineering

> Persona docs and the compendium live in the Obsidian vault (`60-Business/mia-vex/`).

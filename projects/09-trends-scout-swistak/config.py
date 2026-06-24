"""Config for trends_scout — sources, niche, and a free-LLM cascade."""
from pathlib import Path

NICHE = "target consumer niche (configurable)"
REGIONS = ["US", "UK", "DE"]
VAULT_DIR = Path("/root/vault/60-Business/trends-scout")
LOG_DIR = Path("/root/trends_scout/logs")

# Reddit communities scanned via public JSON (no auth required)
REDDIT_SUBS = [
    "BuyItForLife", "ShutUpAndTakeMyMoney", "INeedThis",
    "HomeDecorating", "Frugal", "wellness",
    # ...niche-specific subs configured per campaign
]

GT_SEEDS = [
    "skincare", "home decor", "wellness gadget",
    "beauty tool", "kitchen gadget", "self care",
]

AMAZON_DOMAINS = ["amazon.com", "amazon.de"]
AMAZON_CATEGORIES = ["beauty", "hpc", "home-garden", "luxury-beauty"]

# Free-model cascade on OpenRouter: try each until one responds (resilience + $0 cost)
LLM_MODELS_CASCADE = [
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "openai/gpt-oss-120b:free",
    "z-ai/glm-4.5-air:free",
    "deepseek/deepseek-v4-flash:free",
]

TG_PREFIX = "📈 [Trends]"

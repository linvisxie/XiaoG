"""One place for API price assumptions. Update this file when official prices change.

DeepSeek's published peak prices (USD per 1M tokens), checked 2026-09-11.
The provider returns cached-input tokens separately, so we can estimate both kinds.
"""

DEEPSEEK_PRICING_PER_MILLION = {
    "deepseek-v4-flash": {"input_cache_hit": 0.014, "input_cache_miss": 0.44, "output": 1.32},
    # The API may return this compatible response-model alias even when the
    # request uses deepseek-v4-flash. It has the same published V4 Flash rate.
    "deepseek-flash": {"input_cache_hit": 0.014, "input_cache_miss": 0.44, "output": 1.32},
    "deepseek-v4-pro": {"input_cache_hit": 0.044, "input_cache_miss": 1.32, "output": 3.96},
}


def estimate_deepseek_cost(model: str, usage: dict | None) -> float | None:
    if not usage or model not in DEEPSEEK_PRICING_PER_MILLION:
        return None
    prices = DEEPSEEK_PRICING_PER_MILLION[model]
    hit = int(usage.get("prompt_cache_hit_tokens") or 0)
    prompt = int(usage.get("prompt_tokens") or 0)
    miss = int(usage.get("prompt_cache_miss_tokens") or max(0, prompt - hit))
    output = int(usage.get("completion_tokens") or 0)
    return (hit * prices["input_cache_hit"] + miss * prices["input_cache_miss"] + output * prices["output"]) / 1_000_000

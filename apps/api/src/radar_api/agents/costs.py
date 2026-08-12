from dataclasses import dataclass


SUMMARY_MODEL_PRICES_USD_PER_MILLION = {
    "gpt-5-mini": (0.25, 2.00),
}

TTS_ESTIMATED_USD_PER_MINUTE = {
    "gpt-4o-mini-tts": 0.015,
}


@dataclass(frozen=True)
class TextResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0


def usage_from_response(response) -> tuple[int, int]:
    usage = getattr(response, "usage", None)
    if not usage:
        return 0, 0
    input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", 0) or 0
    return int(input_tokens), int(output_tokens)


def estimate_text_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    input_price, output_price = SUMMARY_MODEL_PRICES_USD_PER_MILLION.get(model, (0.0, 0.0))
    return (input_tokens / 1_000_000 * input_price) + (output_tokens / 1_000_000 * output_price)


def estimate_tts_minutes(text: str) -> float:
    words = len(text.split())
    if not words:
        return 0.0
    return max(1.0, words / 145)


def estimate_tts_cost_usd(model: str, minutes: float) -> float:
    return minutes * TTS_ESTIMATED_USD_PER_MINUTE.get(model, 0.0)

from radar_api.schemas import CollectedItem


def heuristic_scores(item: CollectedItem) -> tuple[float, float, float]:
    reliability = {
        "primary": 9.0,
        "paper": 8.5,
        "press": 6.5,
        "aggregator": 5.5,
        "social": 3.5,
    }.get(item.source_type, 5.0)

    academic_boost = 1.0 if item.category == "academico" else 0.0
    relevance_terms = [
        "agent",
        "model",
        "llm",
        "neural",
        "machine learning",
        "open source",
        "benchmark",
        "inference",
        "reasoning",
        "transformer",
        "arxiv",
        "paper",
        "dataset",
        "evaluation",
        "fine-tuning",
    ]
    haystack = f"{item.title} {item.raw_summary or ''}".lower()
    relevance = min(10.0, 5.0 + academic_boost + sum(0.6 for term in relevance_terms if term in haystack))
    novelty = 8.0 if item.published_at else 6.0
    return relevance, reliability, novelty


def select_top_items(items: list[CollectedItem], limit: int = 12) -> list[CollectedItem]:
    scored = []
    for item in items:
        relevance, reliability, novelty = heuristic_scores(item)
        scored.append((relevance + reliability + novelty, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:limit]]

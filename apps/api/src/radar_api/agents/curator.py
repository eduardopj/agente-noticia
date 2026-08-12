from radar_api.schemas import CollectedItem


def heuristic_scores(item: CollectedItem) -> tuple[float, float, float]:
    reliability = {
        "primary": 9.0,
        "paper": 8.5,
        "press_br": 7.0,
        "press": 6.5,
        "video": 6.0,
        "aggregator": 5.5,
        "social": 3.5,
    }.get(item.source_type, 5.0)

    academic_boost = 0.5 if item.category == "academico" else 0.0
    relevance_terms = [
        "ia",
        "inteligencia artificial",
        "tecnologia",
        "startup",
        "seguranca",
        "ciberseguranca",
        "chip",
        "semicondutor",
        "robos",
        "robotica",
        "computacao",
        "programacao",
        "desenvolvedor",
        "agent",
        "agents",
        "model",
        "llm",
        "ai",
        "artificial intelligence",
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


def _bucket(item: CollectedItem) -> str:
    if item.category == "academico":
        return "academico"
    if item.source_type == "video" or item.category.startswith("video_"):
        return "video"
    if "brasil" in item.category or item.source_type == "press_br":
        return "brasil"
    if item.category in {"ia_global", "open_source", "devtools", "hardware_ia", "seguranca"}:
        return "ia_dev"
    return "mundo"


def select_top_items(items: list[CollectedItem], limit: int = 18) -> list[CollectedItem]:
    scored: list[tuple[float, CollectedItem]] = []
    for item in items:
        relevance, reliability, novelty = heuristic_scores(item)
        scored.append((relevance + reliability + novelty, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)

    quotas = {
        "brasil": 5,
        "ia_dev": 4,
        "mundo": 3,
        "video": 3,
        "academico": 3,
    }
    selected: list[CollectedItem] = []
    selected_urls: set[str] = set()

    for bucket, quota in quotas.items():
        for _, item in scored:
            if len([chosen for chosen in selected if _bucket(chosen) == bucket]) >= quota:
                break
            if item.url in selected_urls or _bucket(item) != bucket:
                continue
            selected.append(item)
            selected_urls.add(item.url)

    for _, item in scored:
        if len(selected) >= limit:
            break
        if item.url in selected_urls:
            continue
        selected.append(item)
        selected_urls.add(item.url)

    return selected[:limit]

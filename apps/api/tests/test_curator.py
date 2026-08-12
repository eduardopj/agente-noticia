from radar_api.agents.curator import heuristic_scores, select_top_items
from radar_api.schemas import CollectedItem


def test_academic_items_receive_relevance_boost():
    item = CollectedItem(
        url="https://arxiv.org/abs/1234.5678",
        title="Large language model agents for education",
        source_name="arXiv",
        source_type="paper",
        category="academico",
    )

    relevance, reliability, novelty = heuristic_scores(item)

    assert relevance >= 6
    assert reliability >= 8
    assert novelty >= 6


def test_select_top_items_limits_results():
    items = [
        CollectedItem(url=f"https://example.com/{index}", title=f"AI item {index}", source_name="Example")
        for index in range(20)
    ]

    selected = select_top_items(items, limit=12)

    assert len(selected) == 12

from sqlalchemy.orm import Session

from radar_api.agents.curator import heuristic_scores
from radar_api.models import Episode, EpisodeItem, SourceItem
from radar_api.schemas import CollectedItem


def upsert_source_items(session: Session, items: list[CollectedItem]) -> list[SourceItem]:
    saved: list[SourceItem] = []
    for item in items:
        existing = session.query(SourceItem).filter(SourceItem.url == item.url).one_or_none()
        relevance, reliability, novelty = heuristic_scores(item)
        if existing:
            saved.append(existing)
            continue
        record = SourceItem(
            url=item.url,
            title=item.title,
            source_name=item.source_name,
            source_type=item.source_type,
            language=item.language,
            category=item.category,
            authors=", ".join(item.authors),
            published_at=item.published_at,
            raw_summary=item.raw_summary,
            relevance_score=relevance,
            reliability_score=reliability,
            novelty_score=novelty,
        )
        session.add(record)
        saved.append(record)
    session.commit()
    for record in saved:
        session.refresh(record)
    return saved


def create_episode(
    session: Session,
    episode_date: str,
    title: str,
    executive_summary: str,
    briefing_markdown: str,
    script_markdown: str,
    audio_url: str | None,
    source_items: list[SourceItem],
) -> Episode:
    existing = session.query(Episode).filter(Episode.episode_date == episode_date).one_or_none()
    if existing:
        existing.title = title
        existing.executive_summary = executive_summary
        existing.briefing_markdown = briefing_markdown
        existing.script_markdown = script_markdown
        existing.audio_url = audio_url
        existing.items.clear()
        episode = existing
    else:
        episode = Episode(
            episode_date=episode_date,
            title=title,
            executive_summary=executive_summary,
            briefing_markdown=briefing_markdown,
            script_markdown=script_markdown,
            audio_url=audio_url,
        )
        session.add(episode)
    session.flush()
    for rank, source_item in enumerate(source_items, start=1):
        episode.items.append(EpisodeItem(source_item_id=source_item.id, rank=rank))
    session.commit()
    session.refresh(episode)
    return episode


def source_to_export(record: SourceItem) -> dict:
    return {
        "id": record.id,
        "title": record.title,
        "url": record.url,
        "source_name": record.source_name,
        "source_type": record.source_type,
        "language": record.language,
        "category": record.category,
        "authors": record.authors,
        "published_at": record.published_at.isoformat() if record.published_at else None,
        "raw_summary": record.raw_summary,
        "curated_summary": record.curated_summary,
        "impact": record.impact,
        "relevance_score": record.relevance_score,
        "reliability_score": record.reliability_score,
        "novelty_score": record.novelty_score,
        "validation_status": record.validation_status,
    }

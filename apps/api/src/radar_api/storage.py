from sqlalchemy.orm import Session

from radar_api.agents.curator import heuristic_scores
from radar_api.models import Episode, EpisodeItem, SourceItem
from radar_api.schemas import CollectedItem
from radar_api.utils.dates import format_datetime_br


def upsert_source_items(session: Session, items: list[CollectedItem]) -> list[SourceItem]:
    saved: list[SourceItem] = []
    for item in items:
        existing = session.query(SourceItem).filter(SourceItem.url == item.url).one_or_none()
        relevance, reliability, novelty = heuristic_scores(item)
        if existing:
            existing.title = item.title
            existing.source_name = item.source_name
            existing.source_type = item.source_type
            existing.language = item.language
            existing.category = item.category
            existing.authors = ", ".join(item.authors)
            existing.published_at = item.published_at or existing.published_at
            existing.updated_at = item.updated_at or existing.updated_at
            existing.raw_summary = item.raw_summary or existing.raw_summary
            existing.relevance_score = relevance
            existing.reliability_score = reliability
            existing.novelty_score = novelty
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
            updated_at=item.updated_at,
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
    summary_input_tokens: int = 0,
    summary_output_tokens: int = 0,
    script_input_tokens: int = 0,
    script_output_tokens: int = 0,
    tts_input_chars: int = 0,
    estimated_audio_minutes: float = 0,
    estimated_cost_usd: float = 0,
    cost_breakdown_json: str | None = None,
) -> Episode:
    existing = session.query(Episode).filter(Episode.episode_date == episode_date).one_or_none()
    if existing:
        existing.title = title
        existing.executive_summary = executive_summary
        existing.briefing_markdown = briefing_markdown
        existing.script_markdown = script_markdown
        existing.audio_url = audio_url
        existing.whatsapp_status = "not_sent"
        existing.summary_input_tokens = summary_input_tokens
        existing.summary_output_tokens = summary_output_tokens
        existing.script_input_tokens = script_input_tokens
        existing.script_output_tokens = script_output_tokens
        existing.tts_input_chars = tts_input_chars
        existing.estimated_audio_minutes = estimated_audio_minutes
        existing.estimated_cost_usd = estimated_cost_usd
        existing.cost_breakdown_json = cost_breakdown_json
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
            summary_input_tokens=summary_input_tokens,
            summary_output_tokens=summary_output_tokens,
            script_input_tokens=script_input_tokens,
            script_output_tokens=script_output_tokens,
            tts_input_chars=tts_input_chars,
            estimated_audio_minutes=estimated_audio_minutes,
            estimated_cost_usd=estimated_cost_usd,
            cost_breakdown_json=cost_breakdown_json,
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
        "published_at_br": format_datetime_br(record.published_at) if record.published_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        "updated_at_br": format_datetime_br(record.updated_at) if record.updated_at else None,
        "raw_summary": record.raw_summary,
        "curated_summary": record.curated_summary,
        "impact": record.impact,
        "relevance_score": record.relevance_score,
        "reliability_score": record.reliability_score,
        "novelty_score": record.novelty_score,
        "validation_status": record.validation_status,
    }

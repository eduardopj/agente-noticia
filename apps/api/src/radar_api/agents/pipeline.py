import asyncio
import json
import re
from pathlib import Path

from radar_api.agents.audio import generate_audio
from radar_api.agents.costs import estimate_text_cost_usd, estimate_tts_cost_usd, estimate_tts_minutes
from radar_api.agents.curator import select_top_items
from radar_api.agents.scriptwriter import generate_script
from radar_api.agents.summarizer import generate_briefing
from radar_api.collectors import collect_arxiv, collect_rss
from radar_api.config import get_settings
from radar_api.db import SessionLocal, init_db
from radar_api.models import Episode, EpisodeItem, SourceItem
from radar_api.storage import create_episode, source_to_export, upsert_source_items
from radar_api.utils.dates import format_date_br, today_local


async def collect_all() -> list:
    rss_items, academic_items = await asyncio.gather(
        collect_rss(),
        collect_arxiv(max_results_per_query=3),
    )
    unique = {item.url: item for item in [*rss_items, *academic_items]}
    return list(unique.values())


async def run_daily_pipeline(target_date: str | None = None):
    init_db()
    episode_date = target_date or today_local().isoformat()
    collected = await collect_all()
    with SessionLocal() as session:
        filtered = filter_previously_used(session, collected, episode_date)
    selected = select_top_items(filtered, limit=18)
    executive, briefing, briefing_result = generate_briefing(selected)
    script_result = generate_script(briefing)
    script = script_result.text
    audio_url = generate_audio(script, episode_date)
    audio_minutes = estimate_tts_minutes(script) if audio_url else 0
    settings = get_settings()
    text_cost = estimate_text_cost_usd(
        settings.openai_summary_model,
        briefing_result.input_tokens + script_result.input_tokens,
        briefing_result.output_tokens + script_result.output_tokens,
    )
    audio_cost = estimate_tts_cost_usd(settings.openai_tts_model, audio_minutes)
    cost_breakdown = {
        "summary_model": settings.openai_summary_model,
        "summary_input_tokens": briefing_result.input_tokens,
        "summary_output_tokens": briefing_result.output_tokens,
        "script_input_tokens": script_result.input_tokens,
        "script_output_tokens": script_result.output_tokens,
        "tts_model": settings.openai_tts_model,
        "tts_input_chars": len(script),
        "estimated_audio_minutes": round(audio_minutes, 2),
        "estimated_text_cost_usd": round(text_cost, 6),
        "estimated_audio_cost_usd": round(audio_cost, 6),
        "estimated_total_cost_usd": round(text_cost + audio_cost, 6),
        "notes": "Audio e estimado porque o endpoint de speech nao retorna uso detalhado.",
    }

    with SessionLocal() as session:
        source_records = upsert_source_items(session, selected)
        episode = create_episode(
            session=session,
            episode_date=episode_date,
            title=f"Radar Tech IA - {format_date_br(episode_date)}",
            executive_summary=executive,
            briefing_markdown=briefing,
            script_markdown=script,
            audio_url=audio_url,
            source_items=source_records,
            summary_input_tokens=briefing_result.input_tokens,
            summary_output_tokens=briefing_result.output_tokens,
            script_input_tokens=script_result.input_tokens,
            script_output_tokens=script_result.output_tokens,
            tts_input_chars=len(script),
            estimated_audio_minutes=audio_minutes,
            estimated_cost_usd=text_cost + audio_cost,
            cost_breakdown_json=json.dumps(cost_breakdown, ensure_ascii=False, indent=2),
        )
        export_episode_artifacts(episode_date, briefing, script, source_records)
        return episode


def filter_previously_used(session, items: list, episode_date: str) -> list:
    used = (
        session.query(SourceItem.url, SourceItem.title)
        .join(EpisodeItem, EpisodeItem.source_item_id == SourceItem.id)
        .join(Episode, Episode.id == EpisodeItem.episode_id)
        .filter(Episode.episode_date != episode_date)
        .all()
    )
    used_urls = {url for url, _ in used}
    used_titles = {_normalize_title(title) for _, title in used}
    fresh = []
    for item in items:
        if item.url in used_urls:
            continue
        if _normalize_title(item.title) in used_titles:
            continue
        fresh.append(item)
    return fresh


def _normalize_title(title: str) -> str:
    lowered = title.lower()
    lowered = re.sub(r"\s+", " ", lowered)
    lowered = re.sub(r"[^\w\s]", "", lowered)
    return lowered.strip()


def export_episode_artifacts(
    episode_date: str,
    briefing: str,
    script: str,
    source_records: list,
) -> None:
    settings = get_settings()
    output_dir = Path(settings.storage_dir) / "episodes" / episode_date
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "briefing.md").write_text(briefing, encoding="utf-8")
    (output_dir / "roteiro.md").write_text(script, encoding="utf-8")
    (output_dir / "fontes.json").write_text(
        json.dumps([source_to_export(record) for record in source_records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

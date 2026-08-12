import asyncio
import json
from pathlib import Path

from radar_api.agents.audio import generate_audio
from radar_api.agents.curator import select_top_items
from radar_api.agents.scriptwriter import generate_script
from radar_api.agents.summarizer import generate_briefing
from radar_api.collectors import collect_arxiv, collect_rss
from radar_api.config import get_settings
from radar_api.db import SessionLocal, init_db
from radar_api.storage import create_episode, source_to_export, upsert_source_items
from radar_api.utils.dates import format_date_br, today_local


async def collect_all() -> list:
    rss_items, academic_items = await asyncio.gather(
        collect_rss(),
        collect_arxiv(),
    )
    unique = {item.url: item for item in [*rss_items, *academic_items]}
    return list(unique.values())


async def run_daily_pipeline(target_date: str | None = None):
    init_db()
    episode_date = target_date or today_local().isoformat()
    collected = await collect_all()
    selected = select_top_items(collected, limit=12)
    executive, briefing = generate_briefing(selected)
    script = generate_script(briefing)
    audio_url = generate_audio(script, episode_date)

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
        )
        export_episode_artifacts(episode_date, briefing, script, source_records)
        return episode


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

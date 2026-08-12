import asyncio

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from radar_api.agents import run_daily_pipeline
from radar_api.config import get_settings
from radar_api.db import get_session, init_db
from radar_api.integrations.evolution import send_audio, send_text
from radar_api.models import Episode, EpisodeItem, SourceItem
from radar_api.schemas import EpisodeResponse, RunJobResponse, SourceResponse, ValidationUpdate
from radar_api.utils.dates import format_date_br

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory=settings.storage_dir), name="static")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.post("/jobs/daily-radar", response_model=RunJobResponse)
async def run_daily_radar() -> RunJobResponse:
    episode = await run_daily_pipeline()
    return RunJobResponse(
        status="ok",
        episode_id=episode.id,
        episode_date=episode.episode_date,
        message="Episodio diario gerado com sucesso",
    )


@app.get("/episodes/latest", response_model=EpisodeResponse)
def latest_episode(session: Session = Depends(get_session)) -> Episode:
    episode = session.query(Episode).order_by(Episode.created_at.desc()).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Nenhum episodio encontrado")
    return episode


@app.get("/episodes/latest/share")
def latest_episode_share(session: Session = Depends(get_session)) -> dict:
    episode = session.query(Episode).order_by(Episode.created_at.desc()).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Nenhum episodio encontrado")
    episode_url = f"{settings.public_app_url}/?date={episode.episode_date}"
    text = (
        f"Bom dia. Seu Radar Tech IA de {format_date_br(episode.episode_date)} esta pronto.\n\n"
        f"{episode.executive_summary}\n\n"
        f"Resumo completo e fontes para validacao:\n{episode_url}"
    )
    return {
        "episode_id": episode.id,
        "number": settings.whatsapp_target_number,
        "text": text,
        "audio_url": episode.audio_url,
        "episode_url": episode_url,
    }


@app.get("/episodes", response_model=list[EpisodeResponse])
def list_episodes(session: Session = Depends(get_session)) -> list[Episode]:
    return session.query(Episode).order_by(Episode.created_at.desc()).limit(30).all()


@app.get("/episodes/{episode_date}", response_model=EpisodeResponse)
def get_episode_by_date(episode_date: str, session: Session = Depends(get_session)) -> Episode:
    episode = session.query(Episode).filter(Episode.episode_date == episode_date).one_or_none()
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio nao encontrado")
    return episode


@app.get("/episodes/{episode_id}/sources", response_model=list[SourceResponse])
def list_episode_sources(episode_id: int, session: Session = Depends(get_session)) -> list[SourceItem]:
    episode = session.get(Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio nao encontrado")
    return (
        session.query(SourceItem)
        .join(EpisodeItem, EpisodeItem.source_item_id == SourceItem.id)
        .filter(EpisodeItem.episode_id == episode_id)
        .order_by(EpisodeItem.rank.asc())
        .all()
    )


@app.get("/sources", response_model=list[SourceResponse])
def list_sources(session: Session = Depends(get_session)) -> list[SourceItem]:
    rows = session.query(SourceItem).order_by(SourceItem.collected_at.desc()).limit(200).all()
    return rows


@app.patch("/sources/{source_id}/validation", response_model=SourceResponse)
def update_source_validation(
    source_id: int,
    payload: ValidationUpdate,
    session: Session = Depends(get_session),
) -> SourceItem:
    allowed = {"pending", "trusted", "doubtful", "discarded"}
    if payload.status not in allowed:
        raise HTTPException(status_code=400, detail="Status de validacao invalido")
    source = session.get(SourceItem, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fonte nao encontrada")
    source.validation_status = payload.status
    session.commit()
    session.refresh(source)
    return source


@app.get("/stats")
def stats(session: Session = Depends(get_session)) -> dict:
    return {
        "episodes": session.query(Episode).count(),
        "sources": session.query(SourceItem).count(),
        "academic_sources": session.query(SourceItem).filter(SourceItem.category == "academico").count(),
        "pending_validation": session.query(SourceItem)
        .filter(SourceItem.validation_status == "pending")
        .count(),
    }


@app.post("/episodes/{episode_id}/mark-sent")
def mark_sent(episode_id: int, session: Session = Depends(get_session)) -> dict:
    episode = session.get(Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio nao encontrado")
    episode.whatsapp_status = "sent"
    session.commit()
    return {"status": "ok"}


@app.post("/deliver/whatsapp/latest")
async def deliver_latest_whatsapp(session: Session = Depends(get_session)) -> dict:
    episode = session.query(Episode).order_by(Episode.created_at.desc()).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Nenhum episodio encontrado")
    if not settings.whatsapp_target_number:
        raise HTTPException(status_code=400, detail="WHATSAPP_TARGET_NUMBER nao configurado")

    share = latest_episode_share(session)
    text_result = await send_text(settings.whatsapp_target_number, share["text"])
    audio_result = None
    if episode.audio_url:
        audio_result = await send_audio(settings.whatsapp_target_number, episode.audio_url)

    episode.whatsapp_status = "sent"
    session.commit()
    return {
        "status": "sent",
        "episode_id": episode.id,
        "sent_audio": bool(audio_result),
        "text_result": text_result,
        "audio_result": audio_result,
    }


def run_sync_job() -> None:
    asyncio.run(run_daily_pipeline())

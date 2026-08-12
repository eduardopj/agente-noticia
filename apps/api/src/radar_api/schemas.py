from datetime import datetime

from pydantic import BaseModel, Field


class CollectedItem(BaseModel):
    url: str
    title: str
    source_name: str
    source_type: str = "unknown"
    language: str = "unknown"
    category: str = "uncategorized"
    authors: list[str] = Field(default_factory=list)
    published_at: datetime | None = None
    raw_summary: str | None = None


class EpisodeResponse(BaseModel):
    id: int
    episode_date: str
    title: str
    executive_summary: str
    briefing_markdown: str
    script_markdown: str | None = None
    audio_url: str | None = None
    whatsapp_status: str
    summary_input_tokens: int = 0
    summary_output_tokens: int = 0
    script_input_tokens: int = 0
    script_output_tokens: int = 0
    tts_input_chars: int = 0
    estimated_audio_minutes: float = 0
    estimated_cost_usd: float = 0
    cost_breakdown_json: str | None = None

    model_config = {"from_attributes": True}


class RunJobResponse(BaseModel):
    status: str
    episode_id: int
    episode_date: str
    message: str


class SourceResponse(BaseModel):
    id: int
    title: str
    url: str
    source_name: str
    source_type: str
    language: str
    category: str
    authors: str | None = None
    published_at: datetime | None = None
    raw_summary: str | None = None
    curated_summary: str | None = None
    impact: str | None = None
    relevance_score: float
    reliability_score: float
    novelty_score: float
    validation_status: str

    model_config = {"from_attributes": True}


class ValidationUpdate(BaseModel):
    status: str

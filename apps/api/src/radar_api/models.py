from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from radar_api.db import Base
from radar_api.utils.dates import format_date_br, format_datetime_br, format_short_date_br


class SourceItem(Base):
    __tablename__ = "source_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(1000), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    source_name: Mapped[str] = mapped_column(String(200))
    source_type: Mapped[str] = mapped_column(String(50), default="unknown")
    language: Mapped[str] = mapped_column(String(20), default="unknown")
    category: Mapped[str] = mapped_column(String(80), default="uncategorized")
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    raw_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    curated_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=0)
    reliability_score: Mapped[float] = mapped_column(Float, default=0)
    novelty_score: Mapped[float] = mapped_column(Float, default=0)
    validation_status: Mapped[str] = mapped_column(String(40), default="pending")

    @property
    def published_at_br(self) -> str | None:
        return format_datetime_br(self.published_at) if self.published_at else None

    @property
    def collected_at_br(self) -> str:
        return format_datetime_br(self.collected_at)


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    episode_date: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    executive_summary: Mapped[str] = mapped_column(Text)
    briefing_markdown: Mapped[str] = mapped_column(Text)
    script_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    whatsapp_status: Mapped[str] = mapped_column(String(40), default="not_sent")
    summary_input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    summary_output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    script_input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    script_output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    tts_input_chars: Mapped[int] = mapped_column(Integer, default=0)
    estimated_audio_minutes: Mapped[float] = mapped_column(Float, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0)
    cost_breakdown_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["EpisodeItem"]] = relationship(
        back_populates="episode",
        cascade="all, delete-orphan",
    )

    @property
    def episode_date_br(self) -> str:
        return format_date_br(self.episode_date)

    @property
    def episode_date_short_br(self) -> str:
        return format_short_date_br(self.episode_date)

    @property
    def created_at_br(self) -> str:
        return format_datetime_br(self.created_at)


class EpisodeItem(Base):
    __tablename__ = "episode_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    episode_id: Mapped[int] = mapped_column(ForeignKey("episodes.id"))
    source_item_id: Mapped[int] = mapped_column(ForeignKey("source_items.id"))
    rank: Mapped[int] = mapped_column(Integer)

    episode: Mapped[Episode] = relationship(back_populates="items")
    source_item: Mapped[SourceItem] = relationship()

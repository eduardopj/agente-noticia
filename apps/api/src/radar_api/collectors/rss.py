from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from radar_api.schemas import CollectedItem
from radar_api.sources import RSS_FEEDS


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except (TypeError, ValueError):
        return None


async def collect_rss(limit_per_feed: int = 5) -> list[CollectedItem]:
    items: list[CollectedItem] = []
    async with httpx.AsyncClient(timeout=20) as client:
        for feed in RSS_FEEDS:
            try:
                response = await client.get(feed["url"], follow_redirects=True)
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            parsed = feedparser.parse(response.content)
            for entry in parsed.entries[:limit_per_feed]:
                items.append(
                    CollectedItem(
                        url=entry.get("link", ""),
                        title=entry.get("title", "Sem titulo"),
                        source_name=feed["name"],
                        source_type=feed["type"],
                        language=feed.get(
                            "language",
                            "pt-BR" if "brasil" in feed["category"] else "en",
                        ),
                        category=feed["category"],
                        authors=[author.get("name", "") for author in entry.get("authors", [])],
                        published_at=_parse_date(entry.get("published") or entry.get("updated")),
                        raw_summary=entry.get("summary"),
                    )
                )
    return [item for item in items if item.url]

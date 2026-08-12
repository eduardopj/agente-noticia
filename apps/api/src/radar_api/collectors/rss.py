from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import feedparser
import httpx

from radar_api.schemas import CollectedItem
from radar_api.sources import RSS_FEEDS

YOUTUBE_FEED = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


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
            url = await _feed_url(client, feed)
            if not url:
                continue
            if feed.get("parser") == "html_listing":
                items.extend(await _collect_html_listing(client, feed, url, limit_per_feed))
                continue
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            parsed = feedparser.parse(response.content)
            for entry in parsed.entries[:limit_per_feed]:
                published_at = _parse_date(entry.get("published"))
                updated_at = _parse_date(entry.get("updated"))
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
                        published_at=published_at or updated_at,
                        updated_at=updated_at,
                        raw_summary=entry.get("summary"),
                    )
                )
    return [item for item in items if item.url]


async def _collect_html_listing(
    client: httpx.AsyncClient,
    feed: dict,
    url: str,
    limit_per_feed: int,
) -> list[CollectedItem]:
    try:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    base_host = urlparse(url).netloc
    soup = BeautifulSoup(response.text, "html.parser")
    collected: list[CollectedItem] = []
    seen: set[str] = set()
    blocked_fragments = [
        "/tags/",
        "/rss",
        "/cupons",
        "/institucional",
        "/minha-serie",
        "/voxel",
        "/webstories",
    ]
    for anchor in soup.find_all("a", href=True):
        title = anchor.get_text(" ", strip=True)
        link = urljoin(url, anchor["href"])
        parsed = urlparse(link)
        if parsed.netloc and parsed.netloc != base_host:
            continue
        if any(fragment in parsed.path for fragment in blocked_fragments):
            continue
        if len(title) < 25 or link in seen:
            continue
        seen.add(link)
        collected.append(
            CollectedItem(
                url=link,
                title=title,
                source_name=feed["name"],
                source_type=feed["type"],
                language=feed.get("language", "pt-BR"),
                category=feed["category"],
                raw_summary=title,
            )
        )
        if len(collected) >= limit_per_feed:
            break
    return collected


async def _feed_url(client: httpx.AsyncClient, feed: dict) -> str | None:
    if feed.get("url"):
        return feed["url"]
    handle = feed.get("youtube_handle")
    if not handle:
        return None
    channel_id = await _youtube_channel_id_from_handle(client, handle)
    return YOUTUBE_FEED.format(channel_id=channel_id) if channel_id else None


async def _youtube_channel_id_from_handle(client: httpx.AsyncClient, handle: str) -> str | None:
    handle = handle.lstrip("@")
    try:
        response = await client.get(f"https://www.youtube.com/@{handle}", follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    match = re.search(r'"channelId":"(UC[a-zA-Z0-9_-]{22})"', response.text)
    if match:
        return match.group(1)
    canonical = re.search(r'<link rel="canonical" href="https://www.youtube.com/channel/(UC[a-zA-Z0-9_-]{22})"', response.text)
    return canonical.group(1) if canonical else None

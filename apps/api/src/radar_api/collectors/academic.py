from datetime import datetime, timedelta
import re
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

import feedparser
import httpx

from radar_api.schemas import CollectedItem
from radar_api.sources import ACADEMIC_PUBLISHERS, ACADEMIC_RSS_FEEDS, ACADEMIC_SEARCH_QUERIES, ARXIV_QUERIES
from radar_api.utils.dates import app_timezone

ARXIV_API = "https://export.arxiv.org/api/query"
CROSSREF_API = "https://api.crossref.org/works"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"
NS = {"atom": "http://www.w3.org/2005/Atom"}


def _text(parent: ET.Element, path: str) -> str | None:
    node = parent.find(path, NS)
    return node.text.strip() if node is not None and node.text else None


def _authors(entry: ET.Element) -> list[str]:
    authors = []
    for author in entry.findall("atom:author", NS):
        name = _text(author, "atom:name")
        if name:
            authors.append(name)
    return authors


def _parse_iso_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _date_parts_to_datetime(parts: list[list[int]] | None) -> datetime | None:
    if not parts:
        return None
    values = parts[0]
    year = values[0] if len(values) > 0 else 1
    month = values[1] if len(values) > 1 else 1
    day = values[2] if len(values) > 2 else 1
    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def _strip_markup(value: str | None) -> str | None:
    if not value:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", text).strip()


def _within_days(value: datetime | None, days: int = 7) -> bool:
    if not value:
        return True
    local_now = datetime.now(app_timezone()).replace(tzinfo=None)
    return local_now - timedelta(days=days) <= value <= local_now + timedelta(days=1)


async def collect_arxiv(max_results_per_query: int = 5) -> list[CollectedItem]:
    collected: list[CollectedItem] = []
    async with httpx.AsyncClient(timeout=25) as client:
        for query in ARXIV_QUERIES:
            url = (
                f"{ARXIV_API}?search_query={quote_plus(query)}"
                f"&start=0&max_results={max_results_per_query}"
                "&sortBy=submittedDate&sortOrder=descending"
            )
            response = await client.get(url)
            response.raise_for_status()
            root = ET.fromstring(response.text)
            for entry in root.findall("atom:entry", NS):
                published = _text(entry, "atom:published")
                updated = _text(entry, "atom:updated")
                collected.append(
                    CollectedItem(
                        url=_text(entry, "atom:id") or "",
                        title=(_text(entry, "atom:title") or "Untitled").replace("\n", " "),
                        source_name="arXiv",
                        source_type="paper",
                        language="en",
                        category="academico",
                        authors=_authors(entry),
                        published_at=_parse_iso_date(published),
                        updated_at=_parse_iso_date(updated),
                        raw_summary=(_text(entry, "atom:summary") or "").replace("\n", " "),
                    )
                )
    unique = {item.url: item for item in collected if item.url}
    return list(unique.values())


async def collect_academic_rss() -> list[CollectedItem]:
    collected: list[CollectedItem] = []
    async with httpx.AsyncClient(timeout=25, follow_redirects=True) as client:
        for source in ACADEMIC_RSS_FEEDS:
            try:
                response = await client.get(
                    source["url"],
                    headers={"User-Agent": "RadarTechIA/1.0 academic briefing"},
                )
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            feed = feedparser.parse(response.text)
            for entry in feed.entries[:8]:
                published = _entry_datetime(entry, "published_parsed")
                updated = _entry_datetime(entry, "updated_parsed")
                if not _within_days(published or updated):
                    continue
                collected.append(
                    CollectedItem(
                        url=entry.get("link") or entry.get("id") or "",
                        title=entry.get("title", "Untitled").strip(),
                        source_name=source["name"],
                        source_type=source["type"],
                        language="en",
                        category=source["category"],
                        authors=_feed_authors(entry),
                        published_at=published,
                        updated_at=updated,
                        raw_summary=_strip_markup(entry.get("summary")),
                    )
                )
    return [item for item in collected if item.url]


def _entry_datetime(entry, field: str) -> datetime | None:
    parsed = entry.get(field)
    if not parsed:
        return None
    return datetime(*parsed[:6])


def _feed_authors(entry) -> list[str]:
    authors = []
    for author in entry.get("authors", []) or []:
        name = author.get("name")
        if name:
            authors.append(name)
    if not authors and entry.get("author"):
        authors.append(entry.get("author"))
    return authors


async def collect_crossref(max_results_per_query: int = 4) -> list[CollectedItem]:
    since = (datetime.now(app_timezone()) - timedelta(days=7)).date().isoformat()
    until = datetime.now(app_timezone()).date().isoformat()
    collected: list[CollectedItem] = []
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for query in ACADEMIC_SEARCH_QUERIES:
            query_count = 0
            try:
                response = await client.get(
                    CROSSREF_API,
                    params={
                        "query": query,
                        "filter": f"from-pub-date:{since},until-pub-date:{until}",
                        "sort": "published",
                        "order": "desc",
                        "rows": str(max_results_per_query * 3),
                    },
                    headers={"User-Agent": "RadarTechIA/1.0 (mailto:radar-tech-ia@example.com)"},
                )
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            for work in response.json().get("message", {}).get("items", []):
                publisher = work.get("publisher") or ""
                venue = (work.get("container-title") or [""])[0]
                if not _is_preferred_academic_source(f"{publisher} {venue}"):
                    continue
                published = (
                    _date_parts_to_datetime(work.get("published-online", {}).get("date-parts"))
                    or _date_parts_to_datetime(work.get("published-print", {}).get("date-parts"))
                    or _date_parts_to_datetime(work.get("published", {}).get("date-parts"))
                )
                updated = _parse_iso_date(work.get("updated", {}).get("date-time")) or _parse_iso_date(
                    work.get("created", {}).get("date-time")
                )
                title = " ".join(work.get("title") or ["Untitled"]).strip()
                doi = work.get("DOI")
                url = f"https://doi.org/{doi}" if doi else work.get("URL", "")
                collected.append(
                    CollectedItem(
                        url=url,
                        title=title,
                        source_name=venue or publisher or "Crossref",
                        source_type="paper",
                        language="en",
                        category="academico",
                        authors=_crossref_authors(work.get("author") or []),
                        published_at=published,
                        updated_at=updated,
                        raw_summary=_strip_markup(work.get("abstract")),
                    )
                )
                query_count += 1
                if query_count >= max_results_per_query:
                    break
    return [item for item in collected if item.url]


def _crossref_authors(authors: list[dict]) -> list[str]:
    names = []
    for author in authors[:8]:
        given = author.get("given", "")
        family = author.get("family", "")
        name = f"{given} {family}".strip()
        if name:
            names.append(name)
    return names


def _is_preferred_academic_source(value: str) -> bool:
    normalized = value.lower()
    return any(publisher.lower() in normalized for publisher in ACADEMIC_PUBLISHERS)


async def collect_semantic_scholar(max_results_per_query: int = 4) -> list[CollectedItem]:
    collected: list[CollectedItem] = []
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for query in ACADEMIC_SEARCH_QUERIES:
            try:
                response = await client.get(
                    SEMANTIC_SCHOLAR_API,
                    params={
                        "query": query,
                        "limit": str(max_results_per_query),
                        "fields": "title,url,abstract,authors,venue,publicationDate,year,externalIds",
                    },
                    headers={"User-Agent": "RadarTechIA/1.0 academic briefing"},
                )
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            for paper in response.json().get("data", []):
                published = _parse_iso_date(paper.get("publicationDate"))
                if not _within_days(published):
                    continue
                external_ids = paper.get("externalIds") or {}
                doi = external_ids.get("DOI")
                url = f"https://doi.org/{doi}" if doi else paper.get("url", "")
                venue = paper.get("venue") or "Semantic Scholar"
                collected.append(
                    CollectedItem(
                        url=url,
                        title=paper.get("title") or "Untitled",
                        source_name=venue,
                        source_type="paper",
                        language="en",
                        category="academico",
                        authors=[author.get("name") for author in paper.get("authors", []) if author.get("name")],
                        published_at=published,
                        updated_at=None,
                        raw_summary=paper.get("abstract"),
                    )
                )
    return [item for item in collected if item.url]


async def collect_academic(max_results_per_query: int = 4) -> list[CollectedItem]:
    results = await asyncio_gather_academic(max_results_per_query)
    unique = {item.url: item for group in results for item in group if item.url}
    return list(unique.values())


async def asyncio_gather_academic(max_results_per_query: int) -> tuple[list[CollectedItem], ...]:
    import asyncio

    return await asyncio.gather(
        collect_arxiv(max_results_per_query=max_results_per_query),
        collect_academic_rss(),
        collect_crossref(max_results_per_query=max_results_per_query),
        collect_semantic_scholar(max_results_per_query=max_results_per_query),
    )

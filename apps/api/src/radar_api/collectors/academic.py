from datetime import datetime
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

import httpx

from radar_api.schemas import CollectedItem
from radar_api.sources import ARXIV_QUERIES

ARXIV_API = "https://export.arxiv.org/api/query"
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
                        published_at=datetime.fromisoformat(published.replace("Z", "+00:00")).replace(tzinfo=None)
                        if published
                        else None,
                        updated_at=datetime.fromisoformat(updated.replace("Z", "+00:00")).replace(tzinfo=None)
                        if updated
                        else None,
                        raw_summary=(_text(entry, "atom:summary") or "").replace("\n", " "),
                    )
                )
    unique = {item.url: item for item in collected if item.url}
    return list(unique.values())

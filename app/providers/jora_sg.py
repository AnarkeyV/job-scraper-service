from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urljoin

import httpx
from bs4 import BeautifulSoup

from app.models import JobResult
from app.providers.base import JobProvider


JORA_BASE_URL = "https://sg.jora.com"


def _build_jora_url(query: str) -> str:
    """
    Build a Jora SG search URL.

    Example:
    Entry Level DevOps Engineer
    -> https://sg.jora.com/Entry-Level-DevOps-Engineer-jobs-in-Singapore
    """
    slug = quote(query.strip().replace(" ", "-"))
    return f"{JORA_BASE_URL}/{slug}-jobs-in-Singapore"


def _clean_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split()).strip()


def _days_from_posted_text(text: str) -> int | None:
    """
    Convert Jora-style text such as:
    - Posted 10h ago
    - Posted 2d ago
    - Posted 3 days ago
    - Posted 1mo ago

    into approximate number of days.
    """
    text = text.lower()

    if "posted" not in text:
        return None

    hour_match = re.search(r"posted\s+(\d+)\s*h", text)
    if hour_match:
        return 0

    day_match = re.search(r"posted\s+(\d+)\s*d", text)
    if day_match:
        return int(day_match.group(1))

    days_match = re.search(r"posted\s+(\d+)\s+days?", text)
    if days_match:
        return int(days_match.group(1))

    month_match = re.search(r"posted\s+(\d+)\s*mo", text)
    if month_match:
        return int(month_match.group(1)) * 30

    if "posted today" in text or "posted just now" in text:
        return 0

    return None


def _extract_posted_text(text: str) -> str:
    match = re.search(
        r"Posted\s+\d+\s*(?:h|d|mo|hours?|days?|months?)\s+ago",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(0)

    if "Posted today" in text:
        return "Posted today"

    return ""


def _infer_work_mode(text: str) -> str:
    lowered = text.lower()

    if "remote" in lowered:
        return "Remote"

    if "hybrid" in lowered:
        return "Hybrid"

    return "On-site/Hybrid"


def _passes_work_mode_filter(text: str, work_mode: str) -> bool:
    lowered = text.lower()

    if work_mode == "remote":
        return "remote" in lowered

    if work_mode == "hybrid":
        return "hybrid" in lowered or "remote" not in lowered

    return True


def _extract_company_and_location(card_text_lines: list[str], title: str) -> tuple[str, str]:
    """
    Best-effort extraction based on visible Jora listing text.

    Jora pages may change their HTML structure, so this intentionally uses
    a tolerant text-line fallback instead of relying on one fragile CSS class.
    """
    cleaned_lines = [_clean_text(line) for line in card_text_lines if _clean_text(line)]

    filtered = []
    for line in cleaned_lines:
        if line.lower() in {"new to you", "save"}:
            continue
        if line == title:
            continue
        if line.startswith("Posted "):
            continue
        filtered.append(line)

    company = filtered[0] if len(filtered) >= 1 else "Unknown company"
    location = filtered[1] if len(filtered) >= 2 else "Singapore"

    return company, location


class JoraSGProvider(JobProvider):
    name = "jora_sg"

    async def search(
        self,
        query: str,
        countries: list[str],
        work_mode: str,
        max_age_days: int,
    ) -> list[JobResult]:
        url = _build_jora_url(query)

        headers = {
            "User-Agent": (
                "job-scraper-service/0.4 "
                "(personal portfolio project; low-frequency local job alert)"
            )
        }

        async with httpx.AsyncClient(timeout=20, headers=headers, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Try common job-card patterns first.
        cards = soup.select(
            "[data-automation='job-card'], "
            "article, "
            "div[data-job-id], "
            "div.job-card"
        )

        # Fallback: build card-like containers from headings if Jora changes markup.
        if not cards:
            headings = soup.find_all(["h2", "h3"])
            cards = []
            for heading in headings:
                parent = heading.find_parent(["article", "div", "section"])
                if parent and parent not in cards:
                    cards.append(parent)

        results: list[JobResult] = []
        seen_urls: set[str] = set()

        for card in cards[:30]:
            card_text = _clean_text(card.get_text(" ", strip=True))
            if not card_text:
                continue

            if not _passes_work_mode_filter(card_text, work_mode):
                continue

            posted_text = _extract_posted_text(card_text)
            posted_days = _days_from_posted_text(posted_text)

            if posted_days is not None and posted_days > max_age_days:
                continue

            title_link = (
                card.select_one("h2 a[href]")
                or card.select_one("h3 a[href]")
                or card.select_one("a[href*='/job/']")
                or card.select_one("a[href]")
            )

            if not title_link:
                continue

            title = _clean_text(title_link.get_text(" ", strip=True))
            href = title_link.get("href", "")

            if not title or not href:
                continue

            job_url = urljoin(JORA_BASE_URL, href)

            if job_url in seen_urls:
                continue

            seen_urls.add(job_url)

            lines = list(card.stripped_strings)
            company, location = _extract_company_and_location(lines, title)

            posted_at = None
            if posted_days is not None:
                posted_at = (datetime.now(timezone.utc) - timedelta(days=posted_days)).date().isoformat()

            results.append(
                JobResult(
                    title=title,
                    company=company,
                    source="Jora SG",
                    location=location,
                    work_mode=_infer_work_mode(card_text),
                    posted_at=posted_at,
                    url=job_url,
                )
            )

        return results
    
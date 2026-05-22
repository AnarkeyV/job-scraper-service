from datetime import datetime, timezone, timedelta
import httpx
from app.models import JobResult
from app.providers.base import JobProvider

class RemoteOKProvider(JobProvider):
    name = "remoteok"

    async def search(self, query: str, countries: list[str], work_mode: str, max_age_days: int):
        url = "https://remoteok.com/api"
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        headers = {"User-Agent": "job-scraper-service/0.1 (+local portfolio project)"}
        async with httpx.AsyncClient(timeout=20, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        q = query.lower()
        results = []
        for item in payload[1:80] if isinstance(payload, list) else []:
            title = item.get("position", "")
            company = item.get("company", "Unknown company")
            tags = " ".join(item.get("tags", []) or [])
            text = f"{title} {company} {tags}".lower()
            if not any(token in text for token in q.split()):
                continue
            try:
                posted = datetime.fromisoformat(item.get("date", "").replace("Z", "+00:00"))
            except Exception:
                posted = datetime.now(timezone.utc)
            if posted < cutoff:
                continue
            location = item.get("location", "Remote") or "Remote"
            results.append(JobResult(
                title=title or "Unknown title",
                company=company,
                source="RemoteOK",
                location=location,
                work_mode="Remote",
                posted_at=posted.date().isoformat(),
                url=item.get("url", ""),
            ))
        return results

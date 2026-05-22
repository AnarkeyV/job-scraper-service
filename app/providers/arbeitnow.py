from datetime import datetime, timezone, timedelta
import httpx
from app.models import JobResult
from app.providers.base import JobProvider

class ArbeitnowProvider(JobProvider):
    name = "arbeitnow"

    async def search(self, query: str, countries: list[str], work_mode: str, max_age_days: int):
        url = "https://www.arbeitnow.com/api/job-board-api"
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        q = query.lower()
        country_terms = [c.lower() for c in countries]
        results = []
        for item in payload.get("data", [])[:100]:
            title = item.get("title", "")
            company = item.get("company_name", "Unknown company")
            location = item.get("location", "") or "Not specified"
            created = item.get("created_at")
            try:
                posted = datetime.fromtimestamp(int(created), timezone.utc)
            except Exception:
                posted = datetime.now(timezone.utc)
            if posted < cutoff:
                continue
            text = f"{title} {company} {location}".lower()
            if not all(part in text for part in q.split()[:2]):
                if q not in text:
                    continue
            if country_terms and not any(c in location.lower() for c in country_terms):
                continue
            remote = bool(item.get("remote"))
            mode = "Remote" if remote else "On-site/Hybrid"
            if work_mode == "remote" and not remote:
                continue
            results.append(JobResult(
                title=title or "Unknown title",
                company=company,
                source="Arbeitnow",
                location=location,
                work_mode=mode,
                posted_at=posted.date().isoformat(),
                url=item.get("url", ""),
            ))
        return results

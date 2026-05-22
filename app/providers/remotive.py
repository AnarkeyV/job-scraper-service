from datetime import datetime, timezone, timedelta
import httpx
from app.models import JobResult
from app.providers.base import JobProvider

class RemotiveProvider(JobProvider):
    name = "remotive"

    async def search(self, query: str, countries: list[str], work_mode: str, max_age_days: int):
        url = "https://remotive.com/api/remote-jobs"
        params = {"search": query}
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        results = []
        for item in payload.get("jobs", [])[:50]:
            candidate_date = item.get("publication_date", "")
            try:
                posted = datetime.fromisoformat(candidate_date.replace("Z", "+00:00"))
            except Exception:
                posted = datetime.now(timezone.utc)
            if posted < cutoff:
                continue
            location = item.get("candidate_required_location", "Remote") or "Remote"
            if countries and not any(c.lower() in location.lower() for c in countries):
                # Remotive frequently returns global remote roles; keep Worldwide/Anywhere roles.
                if not any(token in location.lower() for token in ["worldwide", "anywhere", "remote"]):
                    continue
            results.append(JobResult(
                title=item.get("title", "Unknown title"),
                company=item.get("company_name", "Unknown company"),
                source="Remotive",
                location=location,
                work_mode="Remote",
                posted_at=candidate_date[:10],
                url=item.get("url", ""),
            ))
        return results

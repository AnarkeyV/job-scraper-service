from datetime import date
from app.models import JobResult
from app.providers.base import JobProvider

class MockProvider(JobProvider):
    name = "mock"

    async def search(self, query: str, countries: list[str], work_mode: str, max_age_days: int):
        country = countries[0] if countries else "Singapore"
        mode = "Remote" if work_mode == "remote" else "Hybrid"
        return [
            JobResult(
                title=query.title(),
                company="Demo Cloud Labs",
                source="Mock Provider",
                location=country,
                work_mode=mode,
                posted_at=date.today().isoformat(),
                url="https://example.com/demo-job",
            )
        ]

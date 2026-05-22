from urllib.parse import quote_plus

from app.models import JobResult
from app.providers.base import JobProvider


def _country_label(countries: list[str]) -> str:
    if not countries:
        return "Singapore"
    return ", ".join(countries)


def _work_mode_label(work_mode: str) -> str:
    if not work_mode:
        return "Any"
    return work_mode.replace("_", " ").title()


class SearchLinkProvider(JobProvider):
    """
    Safe link-only provider.

    This provider does not scrape protected job boards.
    It creates direct search links that appear in the report so the user can
    open the relevant job portal search page manually.
    """

    name = "search_links"

    async def search(
        self,
        query: str,
        countries: list[str],
        work_mode: str,
        max_age_days: int,
    ) -> list[JobResult]:
        encoded_query = quote_plus(query)
        country_text = _country_label(countries)
        work_mode_text = _work_mode_label(work_mode)

        links = [
            {
                "title": f"Search MyCareersFuture for {query}",
                "company": "MyCareersFuture",
                "source": "MyCareersFuture",
                "location": country_text,
                "work_mode": work_mode_text,
                "url": f"https://www.mycareersfuture.gov.sg/search?search={encoded_query}&sortBy=new_posting_date&page=0",
            },
            {
                "title": f"Search JobStreet Singapore for {query}",
                "company": "JobStreet Singapore",
                "source": "JobStreet Singapore",
                "location": country_text,
                "work_mode": work_mode_text,
                "url": f"https://sg.jobstreet.com/{encoded_query}-jobs",
            },
            {
                "title": f"Search LinkedIn Jobs for {query}",
                "company": "LinkedIn",
                "source": "LinkedIn",
                "location": country_text,
                "work_mode": work_mode_text,
                "url": f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}&location=Singapore",
            },
            {
                "title": f"Search Jora Singapore for {query}",
                "company": "Jora SG",
                "source": "Jora SG",
                "location": country_text,
                "work_mode": work_mode_text,
                "url": f"https://sg.jora.com/{encoded_query}-jobs",
            },
            {
                "title": f"Search Indeed Singapore for {query}",
                "company": "Indeed SG",
                "source": "Indeed SG",
                "location": country_text,
                "work_mode": work_mode_text,
                "url": f"https://sg.indeed.com/jobs?q={encoded_query}&l=Singapore",
            },
        ]

        return [
            JobResult(
                title=item["title"],
                company=item["company"],
                source=item["source"],
                location=item["location"],
                work_mode=item["work_mode"],
                posted_at=None,
                url=item["url"],
            )
            for item in links
        ]
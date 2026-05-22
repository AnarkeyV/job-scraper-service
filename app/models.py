from dataclasses import dataclass

@dataclass(frozen=True)
class JobResult:
    title: str
    company: str
    source: str
    location: str
    work_mode: str
    posted_at: str
    url: str

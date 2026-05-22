from abc import ABC, abstractmethod
from typing import Iterable
from app.models import JobResult

class JobProvider(ABC):
    name: str

    @abstractmethod
    async def search(self, query: str, countries: list[str], work_mode: str, max_age_days: int) -> Iterable[JobResult]:
        raise NotImplementedError

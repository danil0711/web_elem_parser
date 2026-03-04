from abc import ABC, abstractmethod

class AsyncFetcher(ABC):
    """Асинхронный fetcher для HTML/API."""

    @abstractmethod
    async def fetch(self, url: str) -> str:
        """Возвращает HTML или текст с указанного URL"""
        pass
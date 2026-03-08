import asyncio
import httpx
from typing import Dict, Optional
from app.infrastructure.fetchers.base import AsyncFetcher


class HttpxAsyncFetcher(AsyncFetcher):
    """
    Асинхронный HTTP fetcher с retry, таймаутами и поддержкой прокси.
    """

    def __init__(
        self,
        proxies: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        timeout: int = 30,
    ):
        self.proxies = proxies
        self.max_retries = max_retries
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }

    async def fetch(self, url: str) -> str:
        attempt = 0
        while attempt < self.max_retries:
            try:
                async with httpx.AsyncClient(
                    headers=self.headers, proxy=self.proxies, timeout=self.timeout
                ) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.text
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                attempt += 1
                backoff = 2**attempt
                await asyncio.sleep(backoff)
                if attempt >= self.max_retries:
                    raise e

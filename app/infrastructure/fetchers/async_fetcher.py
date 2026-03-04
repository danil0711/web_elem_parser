import asyncio
import httpx
from typing import Dict, Optional
from app.infrastructure.fetchers.base import AsyncFetcher



class HttpxAsyncFetcher(AsyncFetcher):
    """
    Асинхронный HTTP fetcher с retry, таймаутами и поддержкой прокси.
    """

    def __init__(self,
                 proxies: Optional[Dict[str, str]] = None,
                 max_retries: int = 3,
                 timeout: int = 30):
        self.proxies = proxies
        self.max_retries = max_retries
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            )
        }

    async def fetch(self, url: str) -> str:
        attempt = 0
        while attempt < self.max_retries:
            try:
                async with httpx.AsyncClient(
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=self.timeout
                ) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.text
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                attempt += 1
                backoff = 2 ** attempt
                await asyncio.sleep(backoff)
                if attempt >= self.max_retries:
                    raise e
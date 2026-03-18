import asyncio
import httpx
from app.infrastructure.fetchers.base import AsyncFetcher
from app.infrastructure.http.client import http_client


class HttpxAsyncFetcher(AsyncFetcher):
    """
    Асинхронный HTTP fetcher с retry, таймаутами и поддержкой прокси.
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        max_retries: int = 3,
    ):
        self.client = client
        self.max_retries = max_retries

    async def fetch(self, url: str) -> str:
        attempt = 0

        while attempt < self.max_retries:
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                return response.text

            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                attempt += 1
                backoff = 2**attempt
                await asyncio.sleep(backoff)

                if attempt >= self.max_retries:
                    raise


fetcher = HttpxAsyncFetcher(http_client)

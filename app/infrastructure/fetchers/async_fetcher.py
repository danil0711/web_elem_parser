import httpx

from app.infrastructure.fetchers.base import AsyncFetcher
from app.infrastructure.fetchers.exception import ClientError, SSLError
from app.infrastructure.http.client import http_client


class HttpxAsyncFetcher(AsyncFetcher):
    """
    Асинхронный HTTP fetcher с retry, таймаутами и поддержкой прокси.
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
    ):
        self.client = client

    
    async def fetch(self, url: str) -> str:
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text

        except httpx.ConnectError as e:
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                raise SSLError from e
            raise ConnectionError(str(e)) from e

        except httpx.HTTPStatusError as e:
            status = e.response.status_code

            if 400 <= status < 500:
                raise ClientError(f"HTTP {status}") from e

            raise


fetcher = HttpxAsyncFetcher(http_client)

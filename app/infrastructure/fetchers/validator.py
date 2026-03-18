

import httpx

from app.infrastructure.fetchers.exception import ClientError, SSLError



async def validate_url(fetcher, url: str) -> None:
    try:
        response = await fetcher.client.get(url, timeout=5)

        if 400 <= response.status_code < 500:
            raise ClientError(f"HTTP {response.status_code}")

    except httpx.ConnectError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            raise SSLError(str(e)) from e
        raise ConnectionError(str(e)) from e

    except httpx.RequestError as e:
        raise ConnectionError(str(e)) from e
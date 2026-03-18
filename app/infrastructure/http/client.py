import httpx
import certifi
import ssl

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 ...",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

ssl_context = ssl.create_default_context(cafile=certifi.where())


limits = httpx.Limits(
    max_connections=100,
    max_keepalive_connections=50,
)

http_client = httpx.AsyncClient(
    verify=ssl_context,
    headers=DEFAULT_HEADERS,
    timeout=30,
    limits=limits,
    trust_env=False,
)
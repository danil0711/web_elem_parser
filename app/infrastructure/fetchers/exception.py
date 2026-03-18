class FetcherError(Exception):
    """Базовая ошибка fetcher'а"""
    pass

class SSLError(FetcherError):
    """SSL проблема (сертификат)"""
    pass


class ClientError(FetcherError):
    """4xx ошибки (401, 403, 404)"""
    pass


class ConnectionError(FetcherError):
    """Сетевые проблемы"""
    pass
class HttpClient:
    """Minimal HTTP client placeholder."""

    def get(self, url: str) -> dict:
        return {"url": url, "status": 200}

    def post(self, url: str, payload: dict) -> dict:
        return {"url": url, "status": 200, "payload": payload}

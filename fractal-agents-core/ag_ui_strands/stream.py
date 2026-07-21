class FractalStream:
    """Stream abstraction for event or UI data."""

    def publish(self, message: dict) -> bool:
        return True

    def subscribe(self, channel: str) -> list[dict]:
        return [{"channel": channel, "message": "sample"}]

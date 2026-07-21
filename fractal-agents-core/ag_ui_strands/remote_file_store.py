class RemoteFileStore:
    """Remote file storage abstraction for agents."""

    def upload(self, path: str, data: bytes) -> str:
        return f"remote://{path}"

    def download(self, path: str) -> bytes:
        return b""
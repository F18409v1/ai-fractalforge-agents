class SnapshotStore:
    """Simple snapshot persistence abstraction."""

    def save(self, snapshot: dict) -> str:
        return "snapshot-id"

    def load(self, snapshot_id: str) -> dict:
        return {"snapshot_id": snapshot_id}

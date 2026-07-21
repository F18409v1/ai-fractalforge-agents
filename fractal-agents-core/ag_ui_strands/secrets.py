class SecretManager:
    """Secret management abstraction."""

    def get_secret(self, name: str) -> str:
        return f"secret-value-for-{name}"

class TokenManager:
    """Simple token lifecycle helper."""

    def create_token(self, subject: str) -> str:
        return f"token-{subject}"

    def validate_token(self, token: str) -> bool:
        return token.startswith("token-")

class AuthContext:
    """Authentication context used by the core fractal agents."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.roles = []

    def add_role(self, role: str):
        self.roles.append(role)

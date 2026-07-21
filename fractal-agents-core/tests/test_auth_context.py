from ag_ui_strands.auth_context import AuthContext


def test_auth_context_roles():
    auth = AuthContext(user_id="user-123")
    auth.add_role("tester")
    assert auth.user_id == "user-123"
    assert "tester" in auth.roles

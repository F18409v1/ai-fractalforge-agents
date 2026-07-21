from unittest.mock import MagicMock

import pytest

from src.models import ExperienceAgentConfig, MCPServerConfig, ModelConfig


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""

    return ExperienceAgentConfig(
        memory_id="test-memory-id",
        auth_tenant="test-tenant-id",
        auth_audience="test-audience-id",
        secret_arn="arn:aws:secretsmanager:us-east-1:123:secret:test",
        region="ap-southeast-2",
        http_timeout=30.0,
        model=ModelConfig(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            classification_model_id="anthropic.claude-3-5-haiku-20241022-v1:0",
            max_tokens=4096,
            guardrail_id="test-guardrail-id",
            guardrail_version="1",
        ),
        mcp_server=MCPServerConfig(
            endpoint_url="https://test-mcp.example.com",
            expertise_tool_scope="api://test/.default",
            expertise_tool="get_agent_expertise",
        ),
    )


@pytest.fixture
def mock_mcp_client():
    """Create a mock MCP client with context manager support."""

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=None)

    return mock_client
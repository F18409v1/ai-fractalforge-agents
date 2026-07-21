from typing import Literal

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Model configuration."""

    model_id: str = Field(min_length=1)
    classification_model_id: str = Field(min_length=1)
    max_tokens: int = Field(ge=1)
    guardrail_id: str | None = Field(None, min_length=1)
    guardrail_version: str | None = Field(None, min_length=1)


class MCPServerConfig(BaseModel):
    """MCP Server configuration."""

    endpoint_url: str
    expertise_tool_scope: str
    expertise_tool: str


class ExperienceAgentConfig(BaseModel):
    """Application configuration from environment variables."""

    memory_id: str = Field(min_length=1)
    auth_tenant: str = Field(min_length=1)
    auth_audience: str = Field(min_length=1)
    secret_arn: str = Field(min_length=1)
    region: str = Field(default="ap-southeast-2", min_length=1)
    http_timeout: float = Field(default=30.0)

    model: ModelConfig
    mcp_server: MCPServerConfig


# Structured output models
class AgentInfo(BaseModel):
    """Information about a specialized agent."""

    id: str = Field(
        min_length=1,
        description="Unique identifier for the agent",
    )

    name: str = Field(
        min_length=1,
        description="Display name of the agent",
    )

    mention: str = Field(
        min_length=1,
        description="Mention handle for the agent (e.g., @eps)",
    )

    expertise: str | None = Field(
        None,
        description="Detailed expertise description of the agent",
    )


class ExperienceAgentResponse(BaseModel):
    """Structured output for agent recommendations."""

    agents: list[AgentInfo] = Field(
        default_factory=list,
        description="List of recommended agents matching the user's query",
    )

    content: str = Field(
        min_length=1,
        description="Agent response content (summary or raw text, depending on action)",
    )

    response_quality: Literal[
        "NA",
        "ANSWERED",
        "DEFLECTED",
        "GENERIC",
    ] = Field(
        default="NA",
        description="Quality classification for the returned content",
    )
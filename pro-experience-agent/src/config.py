"""Configuration module for the experience agent."""

import logging
import os
from functools import lru_cache

from .models import ExperienceAgentConfig, MCPServerConfig, ModelConfig

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_agent_config() -> ExperienceAgentConfig:
    """Get the agent configuration from environment variables.

    Returns:
        ExperienceAgentConfig: Agent configuration instance
    """

    config = ExperienceAgentConfig(
        memory_id=os.environ["MEMORY_ID"],
        auth_tenant=os.environ["AUTH_TENANT"],
        auth_audience=os.environ["AUTH_AUDIENCE"],
        secret_arn=os.environ["SECRET_ARN"],
        region=os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-2"),
        http_timeout=float(os.environ.get("HTTP_TIMEOUT", "30.0")),
        model=ModelConfig(
            model_id=os.environ["MODEL_ID"],
            classification_model_id=os.environ["CLASSIFICATION_MODEL_ID"],
            max_tokens=int(os.environ["MAX_TOKENS"]),
            guardrail_id=os.environ.get("GUARDRAIL_ID"),
            guardrail_version=os.environ.get("GUARDRAIL_VERSION"),
        ),
        mcp_server=MCPServerConfig(
            endpoint_url=os.environ["MCP_ENDPOINT_URL"],
            expertise_tool_scope=os.environ["MCP_EXPERTISE_TOOL_SCOPE"],
            expertise_tool=os.environ["MCP_EXPERTISE_TOOL"],
        ),
    )
    logger.debug(
        "Agent configuration loaded: %s",
        config.model_dump(exclude={"secret_arn"})
    )
    return config
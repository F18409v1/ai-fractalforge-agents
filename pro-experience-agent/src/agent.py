"""Experience Agent implementation."""

import asyncio
import logging
import uuid
from typing import Any

import httpx
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)
from bedrock_agentcore.runtime import BedrockAgentCoreContext
from lumina_agents_core.tokens import get_obo_token
from mcp.client.streamable_http import streamable_http_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

from .config import ExperienceAgentConfig
from .models import ExperienceAgentResponse
from .prompt import SYSTEM_PROMPT
from .utils import CLASSIFY_BUFFER_SIZE, classify_response_quality

logger = logging.getLogger(__name__)


async def create_mcp_client(
    user_token: str,
    config: ExperienceAgentConfig,
) -> MCPClient:
    """Create MCP client with OBO token.

    Args:
        user_token: User's JWT token
        config: Agent configuration

    Returns:
        Configured MCP client
    """

    obo_token = await get_obo_token(
        scopes=config.mcp_server.expertise_tool_scope,
        assertion=user_token,
        auth_audience=config.auth_audience,
        auth_tenant=config.auth_tenant,
        secret_ann=config.secret_ann,
    )

    http_client = httpx.AsyncClient(
        timeout=config.http_timeout,
        headers={"Authorization": f"Bearer {obo_token}"},
    )

    return MCPClient(
        lambda: streamable_http_client(
            url=config.mcp_server_endpoint_url,
            http_client=http_client,
        ),
        tool_filters={"allowed": [config.mcp_server.expertise_tool]},
    )


def create_agent(
    user_id: str,
    tools: list,
    config: ExperienceAgentConfig,
) -> Agent:
    """Create configured agent with memory and tools.

    Args:
        user_id: User identifier
        tools: List of available tools
        config: Agent configuration

    Returns:
        Configured Strands agent
    """

    context_session_id = BedrockAgentCoreContext.get_session_id()
    effective_session_id = (
        str(context_session_id)
        if context_session_id
        else str(uuid.uuid4().hex)
    )

    memory_config = AgentCoreMemoryConfig(
        memory_id=config.memory_id,
        session_id=effective_session_id,
        actor_id=user_id,
    )

    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
        region_name=config.region,
    )

    model = BedrockModel(
        model_id=config.model.model_id,
        region_name=config.region,
        max_tokens=config.model.max_tokens,
        guardrail_id=config.model.guardrail_id,
        guardrail_version=config.model.guardrail_version,
        guardrail_latest_message=True,
    )

    return Agent(
        model=model,
        name="experience-agent",
        system_prompt=SYSTEM_PROMPT,
        session_manager=session_manager,
        tools=tools,
        structured_output_model=ExperienceAgentResponse,
    )


async def process_request(
    user_id: str,
    user_token: str,
    user_message: str,
    config: ExperienceAgentConfig,
) -> dict:
    """Process user message and return structured agent recommendations.

    Args:
        user_id: User identifier
        user_token: User's JWT token
        user_message: User's message/prompt
        config: Agent configuration

    Returns:
        Dict with agents and summary fields
    """

    # Create MCP client with user's token
    mcp_client = await create_mcp_client(user_token, config)

    # Keep MCP session open during agent execution
    with mcp_client:
        tools = mcp_client.list_tools_sync()

        agent = create_agent(user_id, tools, config)
        result = await agent.invoke_async(user_message)

        # Return structured JSON response
        response: ExperienceAgentResponse | None = result.structured_output

        if response is None:
            if result.stop_reason == "guardrail_intervened":
                guardrail_message = str(result)

                logger.warning(
                    "Guardrail intervened, returning blocked message: %s",
                    guardrail_message,
                )

                blocked_response = ExperienceAgentResponse(
                    agents=[],
                    content=guardrail_message,
                    response_quality="NA",
                )

                return blocked_response.model_dump()

            logger.error(
                "Agent returned no structured output. Raw result: %s",
                result,
            )

            raise ValueError(
                "Agent failed to produce a structured response"
            )

        quality = "NA"
        if response.content:
            # classify_response_quality performs a blocking boto3 Bedrock call,
            # so run it in a thread to avoid blocking the event loop.
            quality = await asyncio.to_thread(
                classify_response_quality,
                response.content[:CLASSIFY_BUFFER_SIZE],
                model_id=config.model.classification_model_id,
                region=config.region,
            )

        logger.info(
            "Response quality classification: %s (message id=%s)",
            quality,
            result.message_id if hasattr(result, "message_id") else "unknown",
        )

        response.response_quality = quality
        logger.info(
            "Returning structured response: %s",
            response.model_dump(),
        )

        return response.model_dump()
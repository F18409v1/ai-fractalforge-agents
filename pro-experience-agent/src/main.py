"""Entry point for the PRO Experience Agent."""

import asyncio
import logging

from bedrock_agentcore import BedrockAgentCoreApp
from fractal-agents-core.auth_context import get_user_context

from .agent import process_request
from .config import get_agent_config
from .models import ExperienceAgentResponse
from .utils import CLASSIFY_BUFFER_SIZE, classify_response_quality

# Initialize app
app = BedrockAgentCoreApp()
config = get_agent_config()
logger = logging.getLogger(__name__)

logger.info(
    "PRO Experience agent initialized with MCP endpoint: %s",
    config.mcp_server.endpoint_url,
)


@app.entrypoint
async def invoke(payload: dict) -> dict:
    """Main entrypoint for the experience agent.

    Supports two actions:
    - ``invoke_agent`` (default): run the agent for the given ``prompt`` and
      return structured recommendations.
    - ``classify_response_quality``: classify the supplied ``response`` text
      directly without invoking the agent.

    Args:
        payload: Request payload. For ``invoke_agent`` it must contain
            ``prompt``; for ``classify_response_quality`` it must contain
            ``response``.

    Returns:
        Dict containing structured agent recommendations. The classify action
        returns the same ``ExperienceAgentResponse`` shape with the supplied
        text as ``content`` and the classification in ``response_quality``.
    """

    action = payload.get("action", "invoke_agent")

    if action == "classify_response_quality":
        response_text = payload.get("response")

        if not response_text:
            raise ValueError(
                "Missing required field 'response' in payload"
            )

        # classify_response_quality performs a blocking boto3 Bedrock call, so
        # run it in a thread to avoid blocking the event loop.
        quality = await asyncio.to_thread(
            classify_response_quality,
            response_text[:CLASSIFY_BUFFER_SIZE],
            model_id=config.model.classification_model_id,
            region=config.region,
        )

        return ExperienceAgentResponse(
            agents=[],
            content=response_text,
            response_quality=quality,
        ).model_dump()

    if "prompt" not in payload:
        raise ValueError(
            "Missing required field 'prompt' in payload"
        )

    user_message = payload["prompt"]
    user_context = get_user_context()

    return await process_request(
        user_id=user_context["user_id"],
        user_token=user_context["jwt_token"],
        user_message=user_message,
        config=config,
    )


if __name__ == "__main__":
    app.run()
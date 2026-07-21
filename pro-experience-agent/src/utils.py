"""Internal tools for the Experience Agent."""

import logging

import boto3

logger = logging.getLogger(__name__)

# Number of characters to buffer before classifying response quality.
CLASSIFY_BUFFER_SIZE = 300

# Response quality classification prompt.
_RESPONSE_QUALITY_SYSTEM_PROMPT = """You are a response quality classifier.
Given an AI agent's response beginning, classify the response into exactly one category:

- ANSWERED: The response directly addresses the user's question with relevant,
  substantive information. This includes:
  - Providing data, facts, or results that relate to the query
  - Asking the user to disambiguate between multiple matching results
    (e.g. "I found multiple people named X, please select one")
  - Partial answers that still contain useful information about the topic asked

- DEFLECTED: The response refuses or redirects instead of answering. Examples:
  - "I cannot help with that" or "I don't have access to that information"
  - "That question is outside my scope" or "I'm not designed to answer that"
  - Explaining what the agent IS designed for while refusing the actual
    question (e.g. "I'm designed to help with X, not Y")
  - Misinterpreting the question and answering something completely unrelated
    while stating the topic is not in scope
  - Stating no information was found and asking the user to refine their query
    (e.g. "There is no information available about X. If you can provide more
    details, I can try again")

- GENERIC: The response is vague, off-topic, or provides generic filler without
  addressing the specific question. Examples:
  - Boilerplate greetings or pleasantries without substance
  - Repeating the question back without answering
  - Providing unrelated generic information

Respond with ONLY one word: ANSWERED, DEFLECTED, or GENERIC."""


def classify_response_quality(
    agent_response: str,
    model_id: str,
    region: str,
) -> str:
    """Classify response quality based on response text only.

    Args:
        agent_response: The agent response to classify (typically first ~300 chars).
        model_id: Bedrock model id (or inference profile ARN) to use.
        region: AWS region for the Bedrock runtime client.

    Returns:
        One of: ANSWERED, DEFLECTED, GENERIC, or ANSWERED on error.
    """

    try:
        client = boto3.client(
            "bedrock-runtime",
            region_name=region,
        )

        response = client.converse(
            modelId=model_id,
            system=[{"text": _RESPONSE_QUALITY_SYSTEM_PROMPT}],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": (
                                f"Agent response (first {len(agent_response)} chars): "
                                f"{agent_response}"
                            )
                        }
                    ],
                }
            ],
            inferenceConfig={"maxTokens": 10},
        )

        classification = response["output"]["message"]["content"][0]["text"]

        # The model may return trailing punctuation or extra words (e.g.
        # "ANSWERED." or "ANSWERED\nReason: ..."), so parse the first token and
        # strip surrounding punctuation before matching.
        tokens = classification.strip().upper().split()
        result = tokens[0].strip('.,;:!?"\'') if tokens else ""

        if result in {"ANSWERED", "DEFLECTED", "GENERIC"}:
            logger.info(
                "Response quality classification: %s",
                result,
            )
            return result

        logger.warning(
            "Unexpected classification result: %s, defaulting to ANSWERED",
            result,
        )

        return "ANSWERED"

    except Exception as e:
        logger.warning(
            "Response quality classification failed: %s",
            e,
        )
        return "ANSWERED"
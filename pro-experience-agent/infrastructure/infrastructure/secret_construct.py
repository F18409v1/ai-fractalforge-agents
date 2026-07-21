from typing import Literal

from aws_cdk import Tags
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct
from pydantic import BaseModel


class FractalSecretTags(BaseModel):
    tier: Literal["tier0", "tier1", "tier2", "tier3"] = "tier1"
    severity: Literal["high", "low"] = "high"
    access_entity: Literal["service", "human"] = "service"
    rotation: Literal["none", "manual", "auto"] = "manual"


class Secret(secretsmanager.Secret):
    """Construct that creates a secret in AWS Secrets Manager."""

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        scope: Construct,
        construct_id: str,
        secret_name: str,
        description: str | None = None,
        secret_string_value: str | None = None,
        tags: FractalSecretTags = FractalSecretTags(),
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            secret_name=secret_name,
            description=description,
            secret_string_value=secret_string_value,
        )
        Tags.of(self).add("Tier", tags.tier)
        Tags.of(self).add("Severity", tags.severity)
        Tags.of(self).add("AccessEntity", tags.access_entity)
        Tags.of(self).add("Rotation", tags.rotation)

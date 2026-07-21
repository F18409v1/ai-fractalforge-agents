import hashlib
import json
from typing import Any

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_bedrock as bedrock
from constructs import Construct


class VersionedGuardrail(Construct):
    """Construct that creates a Bedrock guardrail and a retained version resource."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id)

        self.guardrail = bedrock.CfnGuardrail(self, "Guardrail", **kwargs)

        # use hash of guardrail props in logical resource id of guardrail version to
        # ensure a new version is created when guardrail configuration changes
        guardrail_fingerprint = hashlib.sha256(
            json.dumps(Stack.of(self).resolve(self.guardrail._cfn_properties), sort_keys=True).encode("utf-8")
        ).hexdigest()[:20]

        self.guardrail_version = bedrock.CfnGuardrailVersion(
            self,
            f"GuardrailVersion{guardrail_fingerprint}",
            guardrail_identifier=self.guardrail.attr_guardrail_id,
        )

        self.guardrail_version.apply_removal_policy(
            RemovalPolicy.RETAIN,
            apply_to_update_replace_policy=True,
        )

    @property
    def attr_guardrail_id(self) -> str:
        return self.guardrail.attr_guardrail_id

    @property
    def attr_guardrail_arn(self) -> str:
        return self.guardrail.attr_guardrail_arn

    @property
    def attr_version(self) -> str:
        return self.guardrail_version.attr_version

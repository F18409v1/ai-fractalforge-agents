import json
from pathlib import Path

from aws_cdk import SecretValue, Stack
from aws_cdk import aws_bedrock as bedrock
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk.aws_bedrockagentcore import CfnMemory, CfnRuntime
from constructs import Construct

from config.models import EnvironmentConfig
from infrastructure.evaluation_construct import DEFAULT_EVALUATORS, BuiltinEvaluator
from infrastructure.guardrail_construct import VersionedGuardrail
from infrastructure.role_construct import AgentCoreRuntimeRole
from infrastructure.secret_construct import Secret


class ExperienceAgentStack(Stack):
    """Stack that creates the Lumina Experience Agent hosted in AgentCore Runtime."""

    def __init__(self, scope: Construct, construct_id: str, config: EnvironmentConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        agent_name = f"experience_agent_{config.stage}".replace("-", "_")

        secret = Secret(
            self,
            "Secret",
            secret_name=f"/{config.stage}/experience_agent",
            description="Secrets for the Lumina Experience Agent",
            secret_string_value=SecretValue.unsafe_plain_text(json.dumps({"client_secret": ""})),
        )

        runtime_role = AgentCoreRuntimeRole(self, "RuntimeRole", role_name=f"{agent_name}_role", description="Role for AgentCore runtime")

        guardrail = VersionedGuardrail(self, "Guardrail", name=f"{agent_name}-guardrail", config_store_path=Path("./guardrails"))

        # evaluation construct can be attached or replaced with a concrete construct instance
        evaluation = DEFAULT_EVALUATORS

        runtime = CfnRuntime(self, "AgentRuntime", runtime_name=agent_name, role_arn=getattr(runtime_role, "role_arn", None))

        self.config = config
        self.components = [secret, runtime_role, guardrail, evaluation, runtime]

    def add_component(self, component) -> None:
        self.components.append(component)

    def describe(self) -> str:
        return f"ExperienceAgentStack({len(self.components)} components, env={getattr(self.config, 'stage', None)})"

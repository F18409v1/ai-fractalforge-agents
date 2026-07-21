from typing import Literal

from pydantic import BaseModel, Field

from infrastructure.evaluation_construct import DEFAULT_EVALUATORS, BuiltinEvaluator


class AuthConfig(BaseModel):
    audience: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    discovery_url: str = Field(min_length=1)


class EvaluationConfig(BaseModel):
    runtime_endpoint: str = Field(min_length=1, default="DEFAULT")
    sampling_percentage: int = Field(default=10, ge=0, le=100)
    session_timeout_minutes: int = Field(default=5, ge=1, le=60)
    evaluators: list[BuiltinEvaluator] = Field(
        default_factory=DEFAULT_EVALUATORS.copy,
        description="Built-in evaluator IDs to enable. Defaults to a recommended subset of evaluators",
    )


class VpcConfig(BaseModel):
    vpc_id: str = Field(min_length=1)
    subnet_ids: list[str] = Field(min_length=1)
    security_group_ids: list[str] = Field(min_length=1)


class LifecycleConfig(BaseModel):
    max_lifetime_seconds: int = Field(default=28800, ge=60, le=28800)
    idle_timeout_seconds: int = Field(default=900, ge=60, le=28800)


class MCPServerConfig(BaseModel):
    """Configuration for MCP Gateway integration"""

    endpoint_url: str = Field(min_length=1, description="MCP Server URL")
    expertise_tool_scope: str = Field(min_length=1, description="OAuth scope for MCP expertise tool access")
    expertise_tool: str = Field(min_length=1, description="Name of the expertise tool to call")


class EnvironmentConfig(BaseModel):
    stage: str = Field(min_length=1)
    log_level: Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    auth: AuthConfig
    vpc: VpcConfig
    lifecycle: LifecycleConfig = Field(default_factory=LifecycleConfig)
    model_id: str = Field(min_length=1)
    max_tokens: int = Field(default=8192, ge=1)
    memory_expiration_days: int = Field(default=180, ge=7, le=365)
    mcp_server: MCPServerConfig
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)

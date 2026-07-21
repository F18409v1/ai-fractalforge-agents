from typing import Literal

from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk.aws_bedrockagentcore import CfnOnlineEvaluationConfig
from constructs import Construct
from pydantic import Field


BuiltinEvaluator = Literal[
    "Builtin.Conciseness",
    "Builtin.Correctness",
    "Builtin.GoalSuccessRate",
    "Builtin.Helpfulness",
    "Builtin.InstructionFollowing",
    "Builtin.ToolParameterAccuracy",
    "Builtin.ToolSelectionAccuracy",
    "Builtin.Faithfulness",
    "Builtin.ResponseRelevance",
    "Builtin.Coherence",
    "Builtin.Refusal",
    "Builtin.Harmfulness",
    "Builtin.Stereotyping",
]


DEFAULT_EVALUATORS: list[BuiltinEvaluator] = [
    "Builtin.Conciseness",
    "Builtin.Correctness",
    "Builtin.GoalSuccessRate",
    "Builtin.Helpfulness",
    "Builtin.InstructionFollowing",
    "Builtin.ToolParameterAccuracy",
    "Builtin.ToolSelectionAccuracy",
]


class EvaluationConstruct(Construct):
    """Construct that creates online evaluation configuration for an AgentCore Runtime."""

    def __init__(
        self,  # noqa: PLR0913, PLR0917
        scope: Construct,
        construct_id: str,
        agent_name: str,
        runtime_id: str,
        inference_profile_arn: str,
        runtime_endpoint: str,
        sampling_percentage: int = Field(default=10, ge=0, le=100),
        session_timeout_minutes: int = Field(default=5, ge=1, le=60),
        evaluators: list[BuiltinEvaluator] = Field(
            default_factory=DEFAULT_EVALUATORS.copy,
            description=(
                "Built-in evaluator IDs to enable. Defaults to a recommended subset of evaluators"
            ),
        ),
    ) -> None:
        super().__init__(scope, construct_id)

        parent_stack = Stack.of(self)
        region = parent_stack.region
        account = parent_stack.account

        resolved_runtime_log_group_name = (
            f"/aws/bedrock-agentcore/runtimes/{runtime_id}-{runtime_endpoint}"
        )

        # ------------------------- IAM role ---------------------------------
        evaluation_role = iam.Role(
            self,
            "EvaluationExecutionRole",
            description=f"IAM role for online evaluation of {agent_name}",
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            assumed_by_conditions={
                "StringEquals": {
                    "aws:SourceAccount": account,
                    "aws:ResourceAccount": account,
                },
                "ArnLike": {
                    "aws:SourceArn": [
                        f"arn:aws:bedrock-agentcore:{region}:{account}:evaluator/*",
                        f"arn:aws:bedrock-agentcore:{region}:{account}:online-evaluation-config/*",
                    ]
                },
            },
            inline_policies={
                "EvaluationPolicy": iam.PolicyDocument(
                    statements=[
                        # CloudWatchLogReadStatement - read/query log groups
                        iam.PolicyStatement(
                            sid="CloudWatchLogReadStatement",
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:DescribeLogGroups",
                                "logs:DescribeLogStreams",
                                "logs:GetQueryResults",
                                "logs:StartQuery",
                                "cloudwatch:GenerateQuery",
                                "cloudwatch:GenerateQueryResultsSummary",
                            ],
                            resources=["*"],
                        ),

                        # CloudWatchLogWriteStatement - write evaluation results log group
                        iam.PolicyStatement(
                            sid="CloudWatchLogWriteStatement",
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                                "logs:GetLogEvents",
                            ],
                            resources=[
                                f"arn:aws:logs:{region}:{account}:log-group:/aws/bedrock-agentcore/evaluations/*",
                            ],
                        ),

                        # CloudWatchIndexPolicyStatement - index policy on spans log group
                        iam.PolicyStatement(
                            sid="CloudWatchIndexPolicyStatement",
                            effect=iam.Effect.ALLOW,
                            actions=["logs:DescribeIndexPolicies", "logs:PutIndexPolicy"],
                            resources=[
                                f"arn:aws:logs:{region}:{account}:log-group:aws/spans",
                                f"arn:aws:logs:{region}:{account}:log-group:aws/spans:*",
                            ],
                        ),

                        # BedrockInvokeStatement - invoke models for LLM-as-judge evaluation
                        iam.PolicyStatement(
                            sid="BedrockInvokeStatement",
                            effect=iam.Effect.ALLOW,
                            actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                            resources=["arn:aws:bedrock:*::foundation-model/*", inference_profile_arn],
                        ),
                    ]
                )
            },
        )

        # --------------------- Online evaluation configuration ----------------
        CfnOnlineEvaluationConfig(
            self,
            "OnlineEvaluationConfig",
            online_evaluation_config_name=f"{agent_name}_evaluation",
            description=f"Online evaluation configuration for the {agent_name}",
            evaluation_execution_role_arn=evaluation_role.role_arn,
            evaluators=[
                CfnOnlineEvaluationConfig.EvaluatorReferenceProperty(evaluator_id=e)
                for e in evaluators
            ],
            data_source_config=CfnOnlineEvaluationConfig.DataSourceConfigProperty(
                cloud_watch_logs=CfnOnlineEvaluationConfig.CloudWatchLogsInputConfigProperty(
                    log_group_names=[resolved_runtime_log_group_name],
                    service_names=[f"{agent_name}.{runtime_endpoint}"],
                )
            ),
            rule=CfnOnlineEvaluationConfig.RuleProperty(
                sampling_config=CfnOnlineEvaluationConfig.SamplingConfigProperty(
                    sampling_percentage=sampling_percentage
                ),
                session_config=CfnOnlineEvaluationConfig.SessionConfigProperty(
                    session_timeout_minutes=session_timeout_minutes
                ),
            ),
        )

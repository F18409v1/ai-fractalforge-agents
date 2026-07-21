from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from constructs import Construct


class AgentCoreRuntimeRole(Construct):
    """Construct that creates an IAM role for AgentCore Runtime with all required permissions."""

    # role based off: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html#runtime-permissions-execut

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        description: str,
        agentcore_memory_arn: str,
    ) -> None:
        super().__init__(scope, construct_id)

        parent_stack = Stack.of(self)
        region = parent_stack.region
        account = parent_stack.account

        self.role = iam.Role(
            self,
            "Role",
            description=description,
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            inline_policies={
                "AgentCoreRuntimeContainerPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            sid="ECRImageAccess",
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ecr:BatchGetImage",
                                "ecr:GetDownloadUrlForLayer",
                            ],
                            resources=[f"arn:aws:ecr:{region}:{account}:repository/*"],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:DescribeLogStreams",
                                "logs:CreateLogGroup",
                            ],
                            resources=[f"arn:aws:logs:{region}:{account}:log-group:/aws/bedrock-agentcore/runtimes/*"],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["logs:DescribeLogGroups"],
                            resources=[f"arn:aws:logs:{region}:{account}:log-group:*"],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=[f"arn:aws:logs:{region}:{account}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"],
                        ),
                        iam.PolicyStatement(
                            sid="ECRTokenAccess",
                            effect=iam.Effect.ALLOW,
                            actions=["ecr:GetAuthorizationToken"],
                            resources=["*"],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "xray:PutTraceSegments",
                                "xray:PutTelemetryRecords",
                                "xray:GetSamplingRules",
                                "xray:GetSamplingTargets",
                            ],
                            resources=["*"],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["cloudwatch:PutMetricData"],
                            resources=["*"],
                            conditions={
                                "StringEquals": {
                                    "cloudwatch:namespace": "bedrock-agentcore"
                                }
                            },
                        ),
                        iam.PolicyStatement(
                            sid="GetAgentAccessToken",
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "bedrock-agentcore:GetWorkloadAccessToken",
                                "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                                "bedrock-agentcore:GetWorkloadAccessTokenForUserId",
                            ],
                            resources=[
                                f"arn:aws:bedrock-agentcore:{region}:{account}:workload-identity-directory/default",
                                f"arn:aws:bedrock-agentcore:{region}:{account}:workload-identity-directory/default/workload-identity/*",
                            ],
                        ),
                        iam.PolicyStatement(
                            sid="BedrockModelInvocation",
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "bedrock:InvokeModel",
                                "bedrock:InvokeModelWithResponseStream",
                            ],
                            resources=[
                                "arn:aws:bedrock:*::foundation-model/*",
                                f"arn:aws:bedrock:{region}:{account}:*",
                            ],
                        ),
                    ]
                )
            },
            # additional policy to facilitate access to Agentcore Memory
            "AgentCoreMemoryPolicy": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "bedrock-agentcore:CreateEvent",
                            "bedrock-agentcore:ListEvents",
                            "bedrock-agentcore:DeleteEvent",
                            "bedrock-agentcore:GetMemory",
                        ],
                        resources=[agentcore_memory_arn],
                    )
                ]
            ),
            # additional policy to facilitate use of Bedrock Guardrails
            "BedrockGuardrailPolicy": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=["bedrock:ApplyGuardrail"],
                        resources=[f"arn:aws:bedrock:{region}:{account}:guardrail/*"],
                    )
                ]
            ),
        }
        
        # Add trust policy conditions for security
        self.role.assume_role_policy.add_statements(
            iam.PolicyStatement(
                sid="AssumeRolePolicy",
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("bedrock-agentcore.amazonaws.com")],
                actions=["sts:AssumeRole"],
                conditions={
                    "StringEquals": {
                        "aws:SourceAccount": account
                    },
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock-agentcore:{region}:{account}:*"
                    }
                }
            )
        )



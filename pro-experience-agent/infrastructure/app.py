#!/usr/bin/env python3
import importlib
import os

import aws_cdk as cdk

from config.models import EnvironmentConfig
from infrastructure.agent_stack import ExperienceAgentStack

app = cdk.App()
env_name = app.node.try_get_context("env")
if not env_name:
    raise ValueError(
        "Missing required CDK context 'env'. Pass it with -c env=<environment> "
        "(e.g. -c env=dev), matching a module in the 'config' package."
    )

env_module_name = str(env_name).replace("-", "_")
config_module = importlib.import_module(f"config.{env_module_name}")
config: EnvironmentConfig = config_module.config

ExperienceAgentStack(app, f"pro-experience-agent-{config.stage}",
    description="Provisions pro Experience Agent resources.",
    config=config,
    tags={
        "AgentName": f"pro_experience_agent_{config.stage}".replace("-", "_"),
        "Automation": "CDK",
        "Environment": config.stage,
        "GitHub": "https://github.com/ai-fractalforge-agents",
    },
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
)

app.synth()

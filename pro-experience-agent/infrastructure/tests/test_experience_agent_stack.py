from infrastructure.infrastructure.agent_stack import ExperienceAgentStack
from infrastructure.config.dev import DevConfig


def test_stack_description():
    stack = ExperienceAgentStack(DevConfig)
    assert "ExperienceAgentStack" in stack.describe()

from config.models import (
    AuthConfig,
    EnvironmentConfig,
    MCPServerConfig,
    VpcConfig,
)

config = EnvironmentConfig(
    stage="dev",
    log_level="DEBUG",
    model_id="au.anthropic.claude-sonnet-4-5-20250929-v1:0",
    max_tokens=8192,
    auth=AuthConfig(
        audience="99b9f448-1ffe-47c1-bfd7-df1d80ee10a5",
        discovery_url="https://login.microsoftonline.com/a3299bba-ade6-4965-b011-bada8d1d9558/v2.0/.well-known/openid-configuration",
        tenant_id="a3299bba-ade6-4965-b011-bada8d1d9558",
    ),
    vpc=VpcConfig(
        vpc_id="vpc-070d7a07bdf4b27a6",
        subnet_ids=["subnet-0372d9196ae2e3109"],
        security_group_ids=["sg-0ee0dc3cbe78a8402"],
    ),
    mcp_server=MCPServerConfig(
        endpoint_url="https://luminamcp-dev.aiknowlg.np.woodside/mcp",
        expertise_tool_scope="api://237f612d-7630-45a2-8661-e14e6cf02144/Experience.Tools.Invoke",
        expertise_tool="get_agent_expertise",
    ),
    memory_expiration_days=7,
)

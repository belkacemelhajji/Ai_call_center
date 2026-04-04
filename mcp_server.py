import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.telecom_tools import (
    lookup_customer, get_service_status,
    create_ticket, check_balance,
    retrieve_faq, handoff_to_human
)

# Tool registry with permissions
TOOL_REGISTRY = {
    "lookup_customer": {
        "function": lookup_customer,
        "allowed_agents": ["orchestrator", "tool_agent", "intent_agent"],
        "description": "Search customer by phone number"
    },
    "get_service_status": {
        "function": get_service_status,
        "allowed_agents": ["orchestrator", "tool_agent"],
        "description": "Get telecom service status"
    },
    "create_ticket": {
        "function": create_ticket,
        "allowed_agents": ["orchestrator", "tool_agent"],
        "description": "Create support ticket"
    },
    "check_balance": {
        "function": check_balance,
        "allowed_agents": ["orchestrator", "tool_agent"],
        "description": "Check customer balance"
    },
    "retrieve_faq": {
        "function": retrieve_faq,
        "allowed_agents": ["orchestrator", "tool_agent", "reception_agent"],
        "description": "Get FAQ answer"
    },
    "handoff_to_human": {
        "function": handoff_to_human,
        "allowed_agents": ["orchestrator", "escalation_agent"],
        "description": "Transfer to human operator"
    }
}

def call_tool(tool_name: str, agent_name: str, params: dict) -> dict:
    """Execute a tool if agent is authorized"""
    if tool_name not in TOOL_REGISTRY:
        return {"success": False, "error": f"Tool '{tool_name}' not found"}

    tool = TOOL_REGISTRY[tool_name]

    if agent_name not in tool["allowed_agents"]:
        return {"success": False, "error": f"Agent '{agent_name}' not authorized for '{tool_name}'"}

    print(f"🔐 MCP Server: {agent_name} → {tool_name}({params})")
    result = tool["function"](**params)
    return result

def list_tools(agent_name: str = None) -> list:
    """List available tools for an agent"""
    tools = []
    for name, info in TOOL_REGISTRY.items():
        if agent_name is None or agent_name in info["allowed_agents"]:
            tools.append({"name": name, "description": info["description"]})
    return tools

if __name__ == "__main__":
    print("=== TEST MCP SERVER ===")
    print("\n📋 All tools:")
    for t in list_tools():
        print(f"  - {t['name']}: {t['description']}")

    print("\n✅ Authorized call:")
    result = call_tool("lookup_customer", "tool_agent", {"phone": "0612345678"})
    print(result)

    print("\n❌ Unauthorized call:")
    result = call_tool("handoff_to_human", "intent_agent", {
        "customer_id": "C001",
        "reason": "test",
        "conversation_summary": "test"
    })
    print(result)
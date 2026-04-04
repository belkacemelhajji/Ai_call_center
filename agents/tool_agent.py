import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
from tools.telecom_tools import (
    lookup_customer, get_service_status,
    create_ticket, check_balance,
    retrieve_faq, handoff_to_human
)

client = Groq(api_key=GROQ_API_KEY)

# Tool registry
TOOLS = {
    "lookup_customer": lookup_customer,
    "get_service_status": get_service_status,
    "create_ticket": create_ticket,
    "check_balance": check_balance,
    "retrieve_faq": retrieve_faq,
    "handoff_to_human": handoff_to_human
}

SYSTEM_PROMPT = """Tu es un agent qui exécute les bons outils télécom selon l'intention détectée.

Selon l'intent reçu, tu dois retourner un JSON avec:
- tool : le nom de l'outil à appeler
- params : les paramètres nécessaires

Outils disponibles:
- lookup_customer(phone) : chercher un client par téléphone
- get_service_status(service) : vérifier l'état d'un service
- create_ticket(customer_id, issue, priority) : créer un ticket
- check_balance(customer_id) : vérifier le solde
- retrieve_faq(topic) : obtenir une réponse FAQ
- handoff_to_human(customer_id, reason, conversation_summary) : transférer à un humain

Réponds UNIQUEMENT avec un JSON valide.
"""

def decide_and_execute_tool(intent_result: dict, conversation_context: str = "") -> dict:
    """Decide which tool to call and execute it"""
    
    prompt = f"""
Intent détecté: {json.dumps(intent_result, ensure_ascii=False)}
Contexte: {conversation_context}

Quel outil appeler et avec quels paramètres ?
"""
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    raw = response.choices[0].message.content.strip()
    
    try:
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        tool_call = json.loads(raw)
    except:
        return {"success": False, "message": "Impossible de déterminer l'outil"}
    
    tool_name = tool_call.get("tool")
    params = tool_call.get("params", {})
    
    print(f"🔧 Tool Agent: calling {tool_name} with {params}")
    
    if tool_name in TOOLS:
        result = TOOLS[tool_name](**params)
        return {"tool_used": tool_name, "params": params, "result": result}
    
    return {"success": False, "message": f"Outil '{tool_name}' non trouvé"}

if __name__ == "__main__":
    # Test
    intent = {
        "intent": "lookup_customer",
        "entities": {"phone": "0612345678"},
        "confidence": "high",
        "language": "fr"
    }
    result = decide_and_execute_tool(intent)
    print(f"\n✅ Tool Result: {result}")
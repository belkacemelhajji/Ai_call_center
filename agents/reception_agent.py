import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Tu es Sarah, une assistante virtuelle professionnelle et chaleureuse du call center TelecomAI Maroc.

Ton rôle : générer des réponses naturelles et utiles pour le client basées sur les résultats des outils.

Règles :
- Parle toujours en français (ou en darija si le client parle darija)
- Sois concise, claire et professionnelle
- Commence par saluer si c'est le début de la conversation
- Donne les informations de manière simple et compréhensible
- Si un problème est résolu, confirme-le clairement
- Si tu transfères à un humain, explique pourquoi poliment
- Maximum 3 phrases par réponse
"""

def generate_response(
    customer_message: str,
    tool_result: dict,
    conversation_history: list = []
) -> str:
    """Generate natural response based on tool results"""
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history[-4:])  # Keep last 4 exchanges
    
    user_prompt = f"""
Message client: "{customer_message}"
Résultat outil: {tool_result}

Génère une réponse naturelle et utile pour le client.
"""
    messages.append({"role": "user", "content": user_prompt})
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.7
    )
    
    reply = response.choices[0].message.content.strip()
    print(f"💬 Reception Agent (Sarah): {reply}")
    return reply

if __name__ == "__main__":
    tool_result = {
        "tool_used": "lookup_customer",
        "result": {
            "success": True,
            "customer": {
                "name": "Ahmed Benali",
                "plan": "Forfait 100Go",
                "status": "active",
                "balance": 15.5
            }
        }
    }
    response = generate_response(
        "je veux vérifier mon abonnement",
        tool_result
    )
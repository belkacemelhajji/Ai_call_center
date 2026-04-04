import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Tu es un agent spécialisé dans l'analyse des intentions des clients d'un call center télécom.

Ton rôle : analyser le message du client et extraire en JSON :
- intent : l'intention principale (lookup_customer, check_service, create_ticket, check_balance, get_faq, handoff, unknown)
- entities : les entités extraites (phone, customer_id, service, topic, etc.)
- confidence : niveau de confiance (high, medium, low)
- language : langue détectée (fr, ar, en)

Réponds UNIQUEMENT avec un JSON valide, sans texte supplémentaire.

Exemples d'intents:
- "je veux vérifier mon abonnement" -> lookup_customer
- "mon internet ne marche pas" -> create_ticket + check_service
- "quel est mon solde" -> check_balance
- "comment résilier" -> get_faq
- "je veux parler à un humain" -> handoff
"""

def analyze_intent(customer_message: str) -> dict:
    """Analyze customer message and extract intent + entities"""
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": customer_message}
        ],
        temperature=0.1
    )
    
    raw = response.choices[0].message.content.strip()
    
    try:
        # Clean possible markdown
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
    except:
        result = {
            "intent": "unknown",
            "entities": {},
            "confidence": "low",
            "language": "fr"
        }
    
    print(f"🧠 Intent Agent: {result}")
    return result

if __name__ == "__main__":
    test_messages = [
        "Bonjour, mon numéro est le 0612345678, je veux vérifier mon abonnement",
        "Mon internet 4G ne fonctionne plus depuis ce matin",
        "Comment est-ce que je peux résilier mon contrat ?",
        "Je veux parler à un conseiller humain"
    ]
    for msg in test_messages:
        print(f"\n💬 Client: {msg}")
        analyze_intent(msg)
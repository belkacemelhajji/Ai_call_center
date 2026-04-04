import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Tu es un agent de supervision qui décide si une conversation doit être escaladée vers un humain.

Analyse la conversation et retourne un JSON avec:
- should_escalate : true ou false
- reason : raison de l'escalade (si applicable)
- urgency : low, medium, high
- summary : résumé court de la situation pour l'opérateur humain

Escalade si:
- Le client est très frustré ou en colère
- Le problème n'a pas été résolu après 2 tentatives
- La demande est hors du scope automatique
- Le client demande explicitement un humain
- Problème de facturation complexe

Réponds UNIQUEMENT avec un JSON valide.
"""

def check_escalation(
    conversation_history: list,
    failed_attempts: int = 0,
    customer_message: str = ""
) -> dict:
    """Check if conversation should be escalated to human"""
    
    prompt = f"""
Historique conversation: {json.dumps(conversation_history[-6:], ensure_ascii=False)}
Tentatives échouées: {failed_attempts}
Dernier message client: "{customer_message}"

Faut-il escalader vers un humain ?
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
        result = json.loads(raw)
    except:
        result = {"should_escalate": False, "reason": "", "urgency": "low", "summary": ""}
    
    if result.get("should_escalate"):
        print(f"🚨 Escalation Agent: ESCALADE REQUISE - {result.get('reason')}")
    else:
        print(f"✅ Escalation Agent: Pas d'escalade nécessaire")
    
    return result
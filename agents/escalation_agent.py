import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Tu es un agent de supervision qui décide si une conversation doit être escaladée vers un humain.

Règles STRICTES pour escalader (should_escalate: true) :
- Le client dit EXPLICITEMENT "je veux un humain" ou "parler à un conseiller"
- Le client est TRÈS en colère avec des insultes
- Le même problème a échoué PLUS DE 3 FOIS
- Problème de facturation très complexe avec litige

NE PAS escalader si :
- Le client dit juste "bonjour"
- C'est le début de la conversation (moins de 2 échanges)
- Le client pose une simple question
- Un problème technique simple est signalé (créer un ticket suffit)

Retourne UNIQUEMENT un JSON valide:
{
  "should_escalate": false,
  "reason": "",
  "urgency": "low",
  "summary": ""
}
"""

def check_escalation(
    conversation_history: list,
    failed_attempts: int = 0,
    customer_message: str = ""
) -> dict:
    """Check if conversation should be escalated to human"""

    # Never escalate if conversation just started
    if len(conversation_history) < 4 and "humain" not in customer_message.lower() and "conseiller" not in customer_message.lower():
        print(f"✅ Escalation Agent: Pas d'escalade nécessaire")
        return {"should_escalate": False, "reason": "", "urgency": "low", "summary": ""}

    # Force escalate if explicitly requested
    escalation_keywords = ["humain", "conseiller", "vrai personne", "agent humain", "parler à quelqu'un"]
    if any(kw in customer_message.lower() for kw in escalation_keywords):
        print(f"🚨 Escalation Agent: Client demande un humain")
        return {
            "should_escalate": True,
            "reason": "Client demande explicitement un opérateur humain",
            "urgency": "high",
            "summary": f"Client a demandé un transfert humain. Dernier message: {customer_message}"
        }

    prompt = f"""
Historique: {json.dumps(conversation_history[-6:], ensure_ascii=False)}
Tentatives échouées: {failed_attempts}
Dernier message: "{customer_message}"

Faut-il escalader ?
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
        print(f"🚨 Escalation Agent: ESCALADE - {result.get('reason')}")
    else:
        print(f"✅ Escalation Agent: Pas d'escalade nécessaire")

    return result
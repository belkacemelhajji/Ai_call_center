import json
import os
import uuid
from datetime import datetime

# Path to data file
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'customers.json')

def load_data():
    """Load data from JSON file"""
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """Save data to JSON file"""
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────
# TOOL 1 — Lookup Customer
# ─────────────────────────────────────────
def lookup_customer(phone: str) -> dict:
    """Search customer by phone number"""
    data = load_data()
    for customer in data['customers']:
        if customer['phone'] == phone:
            return {"success": True, "customer": customer}
    return {"success": False, "message": f"Aucun client trouvé avec le numéro {phone}"}

# ─────────────────────────────────────────
# TOOL 2 — Check Service Status
# ─────────────────────────────────────────
def get_service_status(service: str = None) -> dict:
    """Get status of telecom services"""
    data = load_data()
    services = data['services']
    if service:
        if service in services:
            return {"success": True, "service": service, "status": services[service]}
        return {"success": False, "message": f"Service '{service}' introuvable"}
    return {"success": True, "services": services}

# ─────────────────────────────────────────
# TOOL 3 — Create Ticket
# ─────────────────────────────────────────
def create_ticket(customer_id: str, issue: str, priority: str = "normal") -> dict:
    """Create a support ticket"""
    data = load_data()

    ticket = {
        "id": f"T{str(uuid.uuid4())[:6].upper()}",
        "customer_id": customer_id,
        "issue": issue,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    data['tickets'].append(ticket)
    save_data(data)

    return {"success": True, "ticket": ticket, "message": f"Ticket {ticket['id']} créé avec succès"}

# ─────────────────────────────────────────
# TOOL 4 — Check Balance
# ─────────────────────────────────────────
def check_balance(customer_id: str) -> dict:
    """Check customer account balance"""
    data = load_data()
    for customer in data['customers']:
        if customer['id'] == customer_id:
            return {
                "success": True,
                "customer_id": customer_id,
                "name": customer['name'],
                "balance": customer['balance'],
                "status": customer['status']
            }
    return {"success": False, "message": "Client introuvable"}

# ─────────────────────────────────────────
# TOOL 5 — Get FAQ
# ─────────────────────────────────────────
def retrieve_faq(topic: str) -> dict:
    """Retrieve FAQ answers"""
    faqs = {
        "resiliation": "Pour résilier votre abonnement, appelez le 3000 ou rendez-vous en agence avec votre pièce d'identité.",
        "facture": "Vos factures sont disponibles sur l'application MyTelecom ou sur le site web dans votre espace client.",
        "roaming": "Le roaming est inclus dans les forfaits Illimité et 100Go. Activez-le dans les paramètres de votre compte.",
        "débit": "Si votre débit est lent, redémarrez votre téléphone. Si le problème persiste, signalez-le au 3000.",
        "recharge": "Rechargez votre compte via l'application, les bornes en agence, ou les cartes de recharge disponibles en magasin."
    }

    topic_lower = topic.lower()
    for key, answer in faqs.items():
        if key in topic_lower or topic_lower in key:
            return {"success": True, "topic": key, "answer": answer}

    return {"success": False, "message": "Aucune FAQ trouvée pour ce sujet", "available_topics": list(faqs.keys())}

# ─────────────────────────────────────────
# TOOL 6 — Handoff to Human
# ─────────────────────────────────────────
def handoff_to_human(customer_id: str, reason: str, conversation_summary: str) -> dict:
    """Prepare handoff to human operator"""
    handoff = {
        "id": f"H{str(uuid.uuid4())[:6].upper()}",
        "customer_id": customer_id,
        "reason": reason,
        "summary": conversation_summary,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "waiting_for_operator"
    }
    return {"success": True, "handoff": handoff, "message": "Transfert vers un opérateur humain en cours..."}
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.intent_agent import analyze_intent
from agents.tool_agent import decide_and_execute_tool
from agents.reception_agent import generate_response
from agents.escalation_agent import check_escalation

class Orchestrator:
    def __init__(self):
        self.conversation_history = []
        self.failed_attempts = 0
        self.current_customer = None
        self.call_id = None

    def process_message(self, customer_message: str) -> dict:
        """Main pipeline: message → intent → tool → response"""
        print(f"\n{'='*50}")
        print(f"📞 Customer: {customer_message}")
        print(f"{'='*50}")

        # Step 1 — Analyze intent
        intent = analyze_intent(customer_message)

        # Step 2 — Check escalation first
        escalation = check_escalation(
            self.conversation_history,
            self.failed_attempts,
            customer_message
        )

        if escalation.get("should_escalate"):
            response_text = (
                f"Je comprends votre situation. "
                f"Je vous transfère immédiatement vers un conseiller humain. "
                f"Motif : {escalation.get('reason', 'Demande spéciale')}."
            )
            self._update_history(customer_message, response_text)
            return {
                "response": response_text,
                "intent": intent,
                "tool_result": None,
                "escalated": True,
                "escalation_info": escalation
            }

        # Step 3 — Execute tool
        context = str(self.conversation_history[-2:])
        tool_result = decide_and_execute_tool(intent, context)

        # Track customer
        if tool_result.get("tool_used") == "lookup_customer":
            result = tool_result.get("result", {})
            if result.get("success"):
                self.current_customer = result.get("customer")

        # Step 4 — Generate response
        response_text = generate_response(
            customer_message,
            tool_result,
            self.conversation_history
        )

        # Track failed attempts
        if not tool_result.get("result", {}).get("success", True):
            self.failed_attempts += 1
        else:
            self.failed_attempts = 0

        self._update_history(customer_message, response_text)

        return {
            "response": response_text,
            "intent": intent,
            "tool_result": tool_result,
            "escalated": False
        }

    def _update_history(self, user_msg: str, assistant_msg: str):
        self.conversation_history.append({"role": "user", "content": user_msg})
        self.conversation_history.append({"role": "assistant", "content": assistant_msg})

    def reset(self):
        self.conversation_history = []
        self.failed_attempts = 0
        self.current_customer = None

if __name__ == "__main__":
    orchestrator = Orchestrator()

    test_conversation = [
        "Bonjour, mon numéro est le 0612345678",
        "Est-ce que mon abonnement est actif ?",
        "Mon internet 4G ne fonctionne plus",
        "Je veux parler à un conseiller humain"
    ]

    for message in test_conversation:
        result = orchestrator.process_message(message)
        print(f"🤖 Sarah: {result['response']}")
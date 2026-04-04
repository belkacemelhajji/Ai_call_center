import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import Orchestrator
from agents.logger_agent import LoggerAgent
from voice.stt import listen
from voice.tts import speak

def run_call_center():
    """Main loop: voice input → agents → voice output"""
    orchestrator = Orchestrator()
    logger = LoggerAgent()

    print("\n" + "="*60)
    print("🎙️  TelecomAI Call Center — Démarrage")
    print("="*60)
    speak("Bonjour, bienvenue chez TelecomAI Maroc. Comment puis-je vous aider ?")

    logger.log("call_started", {"call_id": logger.call_id})

    while True:
        print("\n⏳ En attente de votre message... (ou tapez 'quit' pour terminer)")

        # Get input — voice or text
        mode = input("Mode: [v]oix ou [t]exte ? ").strip().lower()

        if mode == "v":
            customer_message = listen(duration=6)
        else:
            customer_message = input("💬 Votre message: ").strip()

        if customer_message.lower() in ["quit", "exit", "fin", "q"]:
            print("\n📞 Fin de l'appel.")
            break

        if not customer_message:
            continue

        # Process through agents
        result = orchestrator.process_message(customer_message)

        # Log the interaction
        logger.log("interaction", {
            "customer_message": customer_message,
            "intent": result.get("intent"),
            "tool_result": result.get("tool_result"),
            "response": result.get("response"),
            "escalated": result.get("escalated")
        })

        # Speak the response
        speak(result["response"])

        # If escalated, end call
        if result.get("escalated"):
            logger.log("escalation", result.get("escalation_info", {}))
            print("\n🚨 Appel transféré à un opérateur humain.")
            break

    # Save artifact
    logger.save_artifact(
        customer_info=orchestrator.current_customer,
        escalated=result.get("escalated", False) if 'result' in dir() else False
    )
    print("\n✅ Artifact sauvegardé dans artifacts/")

if __name__ == "__main__":
    run_call_center()
    
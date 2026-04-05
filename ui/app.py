import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
import threading
from agents.orchestrator import Orchestrator
from agents.logger_agent import LoggerAgent

# Global state
orchestrator = Orchestrator()
logger = LoggerAgent()

def speak_safe(text):
    """TTS safe - ignore errors in thread"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"TTS skipped: {e}")

def speak_async(text):
    """Speak in background"""
    t = threading.Thread(target=speak_safe, args=(text,), daemon=True)
    t.start()

def process_text_message(message, history):
    """Process text message through agents"""
    global orchestrator, logger

    if not message.strip():
        return history, "", "En attente..."

    result = orchestrator.process_message(message)

    logger.log("interaction", {
        "customer_message": message,
        "intent": result.get("intent"),
        "response": result.get("response"),
        "escalated": result.get("escalated")
    })

    response = result["response"]
    speak_async(response)

    # Gradio new format
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})

    intent = result.get("intent", {})
    tool = result.get("tool_result", {})
    escalated = result.get("escalated", False)

    agent_log = f"""🧠 Intent: {intent.get('intent', 'N/A')} ({intent.get('confidence', 'N/A')})
🔧 Tool: {tool.get('tool_used', 'Aucun') if tool else 'Aucun'}
📊 Entités: {intent.get('entities', {})}
🚨 Escalade: {'OUI ⚠️' if escalated else 'Non'}"""

    return history, "", agent_log

def process_voice_message(audio, history):
    """Process voice input"""
    if audio is None:
        return history, "Aucun audio détecté"

    try:
        import whisper
        model = whisper.load_model("small")
        result = model.transcribe(audio, language="fr")
        message = result["text"].strip()
        print(f"🎙️ Transcribed: {message}")
        new_history, _, agent_log = process_text_message(message, history)
        return new_history, agent_log
    except Exception as e:
        return history, f"Erreur audio: {e}"

def reset_conversation():
    """Reset the conversation"""
    global orchestrator, logger
    orchestrator = Orchestrator()
    logger = LoggerAgent()
    return [], "", "✅ Conversation réinitialisée"

def save_artifact():
    """Save call artifact"""
    try:
        filepath = logger.save_artifact(
            customer_info=orchestrator.current_customer,
            escalated=False
        )
        return f"✅ Sauvegardé: {filepath}"
    except Exception as e:
        return f"❌ Erreur: {e}"

# Build UI
with gr.Blocks(title="TelecomAI Call Center") as app:

    gr.Markdown("# 🎙️ TelecomAI Call Center\n### Système multi-agents IA")

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Conversation")
            initial_message = [
               {"role": "assistant", "content": "Bonjour ! Je suis Sarah, votre assistante TelecomAI. Comment puis-je vous aider aujourd'hui ?"}
                      ]
            chatbot = gr.Chatbot(
              value=initial_message,
              height=400,
              label="Sarah - Assistante TelecomAI"
            )

            with gr.Row():
                text_input = gr.Textbox(
                   placeholder="Tapez votre message...",
                   label="",
                   scale=4,
                   interactive=True
                )
                send_btn = gr.Button("Envoyer 📨", scale=1, variant="primary")

            gr.Markdown("### 🎙️ Entrée Voix")
            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="Parlez ici"
            )
            voice_btn = gr.Button("Transcrire & Envoyer 🎙️", variant="secondary")

        with gr.Column(scale=1):
            gr.Markdown("### 🤖 Activité des Agents")
            agent_activity = gr.Textbox(
                label="Logs en temps réel",
                lines=10,
                interactive=False
            )

            gr.Markdown("### 🛠️ Actions")
            reset_btn = gr.Button("🔄 Nouvelle conversation", variant="stop")
            save_btn = gr.Button("💾 Sauvegarder artifact")
            save_output = gr.Textbox(label="Statut", interactive=False)

    gr.Markdown("### 📋 Scénarios de test")
    with gr.Row():
        gr.Examples(
            examples=[
                ["Bonjour, mon numéro est le 0612345678"],
                ["Est-ce que mon abonnement est actif ?"],
                ["Mon internet 4G ne fonctionne plus"],
                ["Comment résilier mon contrat ?"],
                ["Je veux parler à un conseiller humain"],
                ["Quel est mon solde ?"]
            ],
            inputs=text_input
        )

    # Events
    send_btn.click(
        process_text_message,
        inputs=[text_input, chatbot],
        outputs=[chatbot, text_input, agent_activity]
    )
    text_input.submit(
        process_text_message,
        inputs=[text_input, chatbot],
        outputs=[chatbot, text_input, agent_activity]
    )
    voice_btn.click(
        process_voice_message,
        inputs=[audio_input, chatbot],
        outputs=[chatbot, agent_activity]
    )
    reset_btn.click(
        reset_conversation,
        outputs=[chatbot, text_input, agent_activity]
    )
    save_btn.click(
        save_artifact,
        outputs=[save_output]
    )

if __name__ == "__main__":
    print("🚀 Lancement TelecomAI...")
    app.launch(share=False, server_port=7860)
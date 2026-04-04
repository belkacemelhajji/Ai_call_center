import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from agents.orchestrator import Orchestrator
from agents.logger_agent import LoggerAgent
from voice.tts import speak

# Global state
orchestrator = Orchestrator()
logger = LoggerAgent()
chat_history = []

def process_text_message(message, history):
    """Process text message through agents"""
    global orchestrator, logger, chat_history

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
    speak(response)

    history.append((message, response))

    # Build agent activity log
    intent = result.get("intent", {})
    tool = result.get("tool_result", {})
    escalated = result.get("escalated", False)

    agent_log = f"""
🧠 Intent Agent: {intent.get('intent', 'N/A')} (confiance: {intent.get('confidence', 'N/A')})
🔧 Tool Agent: {tool.get('tool_used', 'N/A') if tool else 'Aucun outil'}
🚨 Escalation: {'OUI ⚠️' if escalated else 'Non'}
📊 Entités: {intent.get('entities', {})}
    """.strip()

    return history, "", agent_log

def process_voice_message(audio, history):
    """Process voice input"""
    if audio is None:
        return history, "Aucun audio détecté"

    import whisper
    import soundfile as sf
    import numpy as np

    model = whisper.load_model("small")
    result = model.transcribe(audio, language="fr")
    message = result["text"].strip()

    print(f"🎙️ Transcribed: {message}")
    return process_text_message(message, history)

def reset_conversation():
    """Reset the conversation"""
    global orchestrator, logger, chat_history
    orchestrator = Orchestrator()
    logger = LoggerAgent()
    chat_history = []
    return [], "", "Conversation réinitialisée ✅"

def save_artifact():
    """Save call artifact"""
    filepath = logger.save_artifact(
        customer_info=orchestrator.current_customer,
        escalated=False
    )
    return f"✅ Artifact sauvegardé: {filepath}"

# Build Gradio UI
with gr.Blocks(title="TelecomAI Call Center", theme=gr.themes.Soft()) as app:

    gr.Markdown("""
    # 🎙️ TelecomAI Call Center
    ### Système multi-agents IA pour support télécom
    """)

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Conversation")
            chatbot = gr.Chatbot(height=400, label="Chat avec Sarah (IA)")

            with gr.Row():
                text_input = gr.Textbox(
                    placeholder="Tapez votre message ici...",
                    label="Message texte",
                    scale=4
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
                label="Logs agents en temps réel",
                lines=12,
                interactive=False
            )

            gr.Markdown("### 🛠️ Actions")
            with gr.Row():
                reset_btn = gr.Button("🔄 Nouvelle conversation", variant="stop")
                save_btn = gr.Button("💾 Sauvegarder artifact")

            save_output = gr.Textbox(label="Statut sauvegarde", interactive=False)

    # Example scenarios
    gr.Markdown("### 📋 Scénarios de test rapide")
    with gr.Row():
        gr.Examples(
            examples=[
                ["Bonjour, mon numéro est le 0612345678"],
                ["Est-ce que mon abonnement est actif ?"],
                ["Mon internet 4G ne fonctionne plus depuis ce matin"],
                ["Comment résilier mon contrat ?"],
                ["Je veux parler à un conseiller humain"],
                ["Quel est mon solde ?"]
            ],
            inputs=text_input
        )

    # Wire up events
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
    print("🚀 Lancement de TelecomAI Call Center...")
    app.launch(share=False, server_port=7860)
    
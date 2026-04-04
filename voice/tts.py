import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()

def configure_voice():
    """Set voice properties"""
    engine.setProperty('rate', 150)    # Speed
    engine.setProperty('volume', 0.9)  # Volume

    # Try to set a French voice if available
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break

def speak(text):
    """Convert text to speech"""
    configure_voice()
    print(f"🔊 AI says: {text}")
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    speak("Bonjour, bienvenue chez TelecomAI. Comment puis-je vous aider?")
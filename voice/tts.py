import os
import tempfile
from gtts import gTTS
import pygame

from config import TTS_LANGUAGE

def speak(text, lang=TTS_LANGUAGE):
    """Convert text to speech using gTTS (Google Text-to-Speech) in French"""
    print(f"🔊 AI says: {text}")
    temp_path = None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name
        tts.save(temp_path)

        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
        pygame.mixer.quit()
    except Exception as e:
        print(f"⚠️ TTS error: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    speak("Bonjour, bienvenue chez TelecomAI. Comment puis-je vous aider?")
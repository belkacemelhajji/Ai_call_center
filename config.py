import os
from dotenv import load_dotenv

load_dotenv()

# Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "customers.json")
ARTIFACTS_PATH = os.path.join(BASE_DIR, "artifacts")

# Voice settings
RECORD_DURATION = 6
SAMPLE_RATE = 16000
WHISPER_MODEL = "small"
TTS_LANGUAGE = "fr"  # Language for text-to-speech (French)
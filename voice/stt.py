import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os

# Load Whisper model (small = good balance of speed and accuracy)
model = whisper.load_model("small")

def record_audio(duration=5, sample_rate=16000):
    """Record audio from microphone"""
    print(f"🎙️ Recording for {duration} seconds... Speak now!")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    print("✅ Recording done!")
    return audio, sample_rate

def transcribe_audio(audio, sample_rate):
    """Convert audio to text using Whisper"""
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, sample_rate)
        temp_path = f.name

    # Transcribe
    result = model.transcribe(temp_path, language="fr")
    os.unlink(temp_path)

    return result["text"].strip()

def listen(duration=5):
    """Main function: record and transcribe"""
    audio, sr = record_audio(duration)
    text = transcribe_audio(audio, sr)
    print(f"📝 You said: {text}")
    return text

if __name__ == "__main__":
    listen(duration=5)
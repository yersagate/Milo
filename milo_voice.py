# milo_voice.py
import tempfile
import sounddevice as sd
import scipy.io.wavfile as wav
import pyttsx3

class MiloVoice:
    def __init__(self, client):
        self.client = client

    def record_audio(self, duration=5, samplerate=16000):
        """Records audio from the microphone to a temporary WAV file."""
        print(f"Listening for {duration} seconds...")
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        wav.write(temp_file.name, samplerate, audio_data)
        return temp_file.name

    def transcribe(self, audio_path):
        """Sends audio file to Groq Whisper API for transcription."""
        with open(audio_path, "rb") as file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=file
            )
        return transcript.text

    def speak(self, text):
        """Speaks out text using a local text-to-speech engine."""
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

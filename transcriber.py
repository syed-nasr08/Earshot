"""Local speech-to-text using faster-whisper. No audio leaves the machine."""
from faster_whisper import WhisperModel

from config import WHISPER_MODEL


class Transcriber:
    def __init__(self):
        print(f"Loading Whisper model '{WHISPER_MODEL}' (first run downloads it)...")
        self.model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")

    def transcribe(self, audio) -> str:
        segments, _ = self.model.transcribe(audio, language="en", vad_filter=False)
        return " ".join(seg.text.strip() for seg in segments).strip()

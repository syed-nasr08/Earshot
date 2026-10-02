"""Central configuration. Values can be overridden via a .env file."""
import os

from dotenv import load_dotenv

load_dotenv()

# --- OpenRouter (answer generation) -----------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-5")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# --- Local transcription (faster-whisper) -----------------------------------
# Options, small->large: tiny.en, base.en, small.en, medium.en
# Default is small.en because audio comes phone-speaker -> laptop mic (noisier).
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small.en")

# --- Audio + voice-activity detection ---------------------------------------
SAMPLE_RATE = 16000          # webrtcvad supports 8/16/32/48 kHz
FRAME_MS = 30                # webrtcvad supports 10/20/30 ms frames
VAD_AGGRESSIVENESS = int(os.getenv("VAD_AGGRESSIVENESS", "2"))  # 0-3, higher = stricter
SILENCE_MS = int(os.getenv("SILENCE_MS", "900"))      # trailing silence that ends a question
MIN_SPEECH_MS = int(os.getenv("MIN_SPEECH_MS", "400"))  # ignore blips shorter than this

# Input device: leave empty for the system default mic, or set to a device index
# or a substring of its name (e.g. "MacBook"). Run `python main.py --list-devices`.
_dev = os.getenv("INPUT_DEVICE", "").strip()
INPUT_DEVICE = int(_dev) if _dev.isdigit() else (_dev or None)

# --- Output document ---------------------------------------------------------
DOC_PATH = os.getenv(
    "DOC_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "interview_answers.docx"),
)

# --- Google Doc output (optional) -------------------------------------------
# If GDOC_WEBAPP_URL is set, answers go to your Google Doc via an Apps Script
# web app instead of the local .docx. GDOC_SECRET must match the SECRET in the
# script. See google_apps_script.gs for setup.
GDOC_WEBAPP_URL = os.getenv("GDOC_WEBAPP_URL", "").strip()
GDOC_SECRET = os.getenv("GDOC_SECRET", "").strip()

# --- Noise filtering ---------------------------------------------------------
# Whisper tends to emit these short phrases on silence/noise. Drop them so a
# stray sound doesn't trigger a phantom question and a wasted API call.
HALLUCINATION_PHRASES = {
    "thank you.",
    "thanks for watching!",
    "thank you for watching.",
    "you",
    "bye.",
    ".",
    "so",
    "okay.",
}

# --- Answer style ------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are assisting a candidate during a live interview. "
    "Given an interview question, reply with a concise, well-structured answer "
    "written in paragraph form that the candidate could speak aloud naturally. "
    "Use plain, confident language. Do not use bullet points, headings, or "
    "preambles like 'Great question'. Keep it to 2-4 short paragraphs at most."
)

"""Interview Helper — listen to a spoken question, write a concise answer to a Word doc.

Flow: mic -> voice-activity detection -> local Whisper transcription ->
OpenRouter answer -> append to .docx. Press F9 to clear the doc, Ctrl+C to quit.
"""
import sys

from answer_engine import AnswerEngine
from audio_capture import AudioCapture, list_input_devices
from config import DOC_PATH, GDOC_WEBAPP_URL, HALLUCINATION_PHRASES, OPENROUTER_MODEL
from hotkey import HotkeyListener
from transcriber import Transcriber


def build_writer():
    """Google Doc if configured, otherwise the local .docx."""
    if GDOC_WEBAPP_URL:
        from gdoc_writer import GoogleDocWebAppWriter
        return GoogleDocWebAppWriter(), "Google Doc (Apps Script web app)"
    from doc_writer import DocWriter
    return DocWriter(), f"local docx -> {DOC_PATH}"


def main():
    if "--list-devices" in sys.argv:
        print(list_input_devices())
        return

    print("=" * 62)
    print("  Interview Helper — spoken question -> answer")
    print("=" * 62)

    # Fail fast on missing key before loading the (slow) Whisper model.
    engine = AnswerEngine()
    transcriber = Transcriber()
    writer, dest_label = build_writer()
    hotkeys = HotkeyListener(on_clear=writer.clear)
    capture = AudioCapture()

    hotkeys.start()
    capture.start()

    print(f"\nModel:   {OPENROUTER_MODEL}")
    print(f"Writing: {dest_label}")
    print("\nListening… ask your question out loud.")
    print("  F9     = clear the document")
    print("  Ctrl+C = quit\n")

    try:
        for audio in capture.segments():
            question = transcriber.transcribe(audio)
            if not question or len(question) < 3:
                continue
            if question.strip().lower() in HALLUCINATION_PHRASES:
                continue  # noise blip, not a real question
            print(f"\n❓ {question}")
            print("   …thinking…")
            try:
                answer = engine.answer(question)
            except Exception as exc:
                print(f"   ⚠️  answer error: {exc}")
                continue
            writer.append(question, answer)
            preview = answer[:80].replace("\n", " ")
            print(f"   ✅ written: {preview}…")
    except KeyboardInterrupt:
        print("\nStopping…")
    finally:
        capture.stop()
        hotkeys.stop()


if __name__ == "__main__":
    main()

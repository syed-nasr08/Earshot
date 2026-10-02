# earshot

Listens to a spoken question through your Mac's microphone, transcribes it
locally, gets a concise paragraph-form answer from an AI model via OpenRouter,
and appends it to a Word document.

- **Transcription** runs locally (faster-whisper) — your audio never leaves the machine.
- **Answers** come from OpenRouter using your API key.
- **F9** clears the whole document to start a fresh session.

## Setup

```bash
git clone https://github.com/syed-nasr08/earshot.git
cd earshot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and paste your OpenRouter key
```

## macOS permissions (one time)

Run the app once, then grant the Terminal app (or your IDE) these under
**System Settings → Privacy & Security**:

- **Microphone** — required to hear questions.
- **Accessibility** and **Input Monitoring** — required for the global **F9** hotkey.

You may need to quit and reopen the terminal after granting them.

## Run

```bash
source venv/bin/activate
python main.py
```

Speak your question, pause, and the answer is written to
`interview_answers.docx`. Press **F9** to clear it. **Ctrl+C** to quit.

## Configuration

All options live in `.env` (see `.env.example`):

- `OPENROUTER_MODEL` — any OpenRouter chat model. If the default 404s, pick
  another from https://openrouter.ai/models (e.g. `openai/gpt-4o`).
- `WHISPER_MODEL` — `tiny.en` is fastest, `small.en`/`medium.en` are more
  accurate but slower.
- `VAD_AGGRESSIVENESS`, `SILENCE_MS`, `MIN_SPEECH_MS` — tune if it triggers on
  background noise or cuts you off mid-question.

## Capturing audio from a phone speaker

The intended setup is: interview audio plays from your **phone speaker**, and
your **laptop's built-in mic** picks it up. Two things matter for this to work:

- **Turn OFF Voice Isolation.** In Control Center → Microphone Mode, choose
  **Standard**. Voice Isolation treats the phone speaker as background noise and
  will suppress the very audio you want to capture.
- **Placement & volume.** Put the phone close to the laptop and keep the room
  quiet; speaker→mic audio is lower quality, which is why the default Whisper
  model is `small.en`. Bump to `medium.en` in `.env` if accuracy is poor.
- **Pick the mic explicitly** if the default isn't the built-in one:
  `python main.py --list-devices`, then set `INPUT_DEVICE` in `.env`.

## Output to a Google Doc (optional)

By default answers go to a local `.docx`. To send them to a Google Doc instead:

1. Open the target Google Doc → **Extensions → Apps Script**.
2. Paste in `google_apps_script.gs`, change `SECRET` to any phrase.
3. **Deploy → New deployment → Web app**, *Execute as: Me*, *Who has access:
   Anyone*. Authorize it. Copy the `/exec` URL.
4. In `.env` set `GDOC_WEBAPP_URL` (the /exec URL) and `GDOC_SECRET` (same phrase).

The app auto-switches to the Google Doc when `GDOC_WEBAPP_URL` is present. **F9**
clears the Google Doc just like the local file.

## Notes & limits

- **Keep the .docx closed in Word while running.** Word does not auto-reload an
  externally changed file, and saving from Word can overwrite the app's writes.
  Open it to review after a session, or reopen to see new answers.
- Continuous listening can mis-trigger on background noise or a long mid-sentence
  pause. Raise `VAD_AGGRESSIVENESS` or `SILENCE_MS` if that happens.
- There's a few-seconds delay per answer (transcription + model call).
